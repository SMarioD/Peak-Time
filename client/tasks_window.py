import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QListWidget, QListWidgetItem, QDialog
from PyQt5.QtCore import Qt
from update_task_status_dialog import UpdateTaskStatusDialog


class TasksWindow(QWidget):
    def __init__(self, jwt_token, user_id):
        super().__init__()
        self.jwt_token = jwt_token
        self.user_id = user_id
        self.setWindowTitle(f"Sarcinile Utilizatorului ID: {self.user_id}")
        self.setGeometry(150, 150, 600, 400)
        self.initUI()
        self.load_tasks()

    def initUI(self):
        layout = QVBoxLayout()
        self.tasks_list_widget = QListWidget()
        self.tasks_list_widget.itemDoubleClicked.connect(self.on_task_selected)
        layout.addWidget(QLabel("Sarcinile tale (dublu-clic pentru a actualiza):"))
        layout.addWidget(self.tasks_list_widget)
        self.setLayout(layout)

    def load_tasks(self):
        tasks_url = "http://localhost:8080/api/v1/tasks/mytasks"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(tasks_url, headers=headers)
            self.tasks_list_widget.clear()
            if response.status_code == 200:
                tasks = response.json()
                if not tasks:
                    self.tasks_list_widget.addItem("Nu ai sarcini atribuite.")
                else:
                    for task in tasks:
                        item_text = f"[{task.get('status').upper()}] {task.get('titlu')}"
                        list_item = QListWidgetItem(item_text)
                        list_item.setData(Qt.UserRole, task)
                        self.tasks_list_widget.addItem(list_item)
            else:
                self.tasks_list_widget.addItem(f"Eroare la încărcarea sarcinilor (Status: {response.status_code}).")
        except requests.exceptions.RequestException:
            self.tasks_list_widget.addItem("Eroare de conexiune.")

    def on_task_selected(self, item):
        task_data = item.data(Qt.UserRole)
        if not task_data:
            return
        dialog = UpdateTaskStatusDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            new_status = dialog.get_selected_status()
            if new_status:
                self.handle_update_task(task_data.get('id'), new_status)

    def handle_update_task(self, task_id, new_status):
        update_url = f"http://localhost:8080/api/v1/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        payload = {"status": new_status}
        try:
            response = requests.put(update_url, headers=headers, json=payload)
            if response.status_code == 200:
                QMessageBox.information(self, "Succes", "Statusul sarcinii a fost actualizat.")
                self.load_tasks()  # Reîmprospătăm lista
            else:
                QMessageBox.critical(self, "Eroare", f"Nu s-a putut actualiza statusul: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))