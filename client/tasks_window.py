import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QMessageBox, QListWidget,
                             QListWidgetItem, QDialog, QHBoxLayout)
from PyQt5.QtCore import Qt

from theme import SuccessDialog
from update_task_status_dialog import UpdateTaskStatusDialog
from gantt_window import GanttWindow


class TasksWindow(QWidget):
    def __init__(self, jwt_token, user_id):
        super().__init__()
        self.jwt_token = jwt_token
        self.user_id = user_id
        self.setWindowTitle("Lista de sarcini")
        self.setGeometry(150, 150, 850, 500)
        self.initUI()
        self.load_tasks()

    def initUI(self):
        layout = QVBoxLayout()
        content_layout = QHBoxLayout()

        self.tasks_list_widget = QListWidget()
        self.tasks_list_widget.setStyleSheet("""
            QListWidget { background-color: #2b2b2b; border: 1px solid #444; border-radius: 5px; color: white; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #333; }
            QListWidget::item:selected { background-color: #007ACC; color: white; }
        """)
        self.tasks_list_widget.itemClicked.connect(self.show_task_details)
        self.tasks_list_widget.itemDoubleClicked.connect(self.on_task_selected)

        self.details_panel = QLabel("Selectați o sarcină pentru a vedea detaliile...")
        self.details_panel.setWordWrap(True)
        self.details_panel.setAlignment(Qt.AlignTop)
        self.details_panel.setStyleSheet("""
            QLabel { 
                background-color: #1e1e1e; 
                padding: 20px; 
                border-radius: 10px; 
                border: 1px solid #007ACC;
                font-family: 'Segoe UI';
                color: white;
            }
        """)

        content_layout.addWidget(self.tasks_list_widget, 2)
        content_layout.addWidget(self.details_panel, 3)

        layout.addLayout(content_layout)
        self.setLayout(layout)

    def show_task_details(self, item):
        task = item.data(Qt.UserRole)

        if task is None:
            self.details_panel.setText("Selectați o sarcină validă pentru a vedea detaliile.")
            return
        prio_color = "#ff4444" if task.get('prioritate') == 'CRITICA' else "#00ff00" if task.get(
            'prioritate') == 'MICA' else "#ffaa00"
        card_html = f"""
        <div style='color: white;'>
            <h1 style='color: #007ACC; margin-bottom: 5px;'>{task.get('titlu')}</h1>
            <p style='color: #888; font-size: 12px;'>STATUS: <b style='color: white;'>{task.get('status').upper()}</b></p>
            <hr style='border: 1px solid #444;'>

            <table width='100%' style='margin-top: 10px;'>
                <tr>
                    <td width='40%'><b style='color: #aaa;'>Prioritate:</b></td>
                    <td><span style='color: {prio_color}; font-weight: bold;'>{task.get('prioritate')}</span></td>
                </tr>
                <tr>
                    <td><b style='color: #aaa;'>Timp Estimat (PERT):</b></td>
                    <td><span style='color: #00ff00; font-weight: bold;'>{task.get('durataEstimataFinala', 0):.2f} ore</span></td>
                </tr>
            </table>

            <br>
            <div style='background-color: #2d2d2d; padding: 15px; border-radius: 8px;'>
                <b style='color: #007ACC;'>DESCRIERE DETALIATĂ:</b><br>
                <p style='color: #dcdcdc; line-height: 1.5; margin-top: 10px;'>
                    {task.get('descriere') or '<i>Nicio descriere furnizată pentru această sarcină.</i>'}
                </p>
            </div>
        </div>
        """
        self.details_panel.setText(card_html)

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
                        status_icon = "⏳" if task.get('status') == 'in asteptare' else "⚙️"
                        item_text = f"{status_icon} {task.get('titlu')}"
                        list_item = QListWidgetItem(item_text)
                        list_item.setData(Qt.UserRole, task)
                        self.tasks_list_widget.addItem(list_item)
        except:
            self.tasks_list_widget.addItem("Eroare de conexiune.")

    def on_task_selected(self, item):
        task_data = item.data(Qt.UserRole)
        if not task_data: return
        dialog = UpdateTaskStatusDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_status = dialog.get_selected_status()
            if new_status:
                self.handle_update_task(task_data.get('id'), new_status)

    def on_task_double_clicked(self, item):
        task_data = item.data(Qt.UserRole)
        if task_data is None: return

        p_id = task_data.get('projectId')
        if p_id:
            self.gantt_win = GanttWindow(
                project_id=p_id,
                token=self.jwt_token,
                project_name=f"Proiect #{p_id} (via {task_data.get('titlu')})"
            )
            self.gantt_win.show()

    def handle_update_task(self, task_id, new_status):
        update_url = f"http://localhost:8080/api/v1/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            res = requests.put(update_url, headers=headers, json={"status": new_status})
            if res.status_code == 200:
                SuccessDialog("Status actualizat.", self).exec_()
                self.load_tasks()
            else:
                error_msg = res.json().get('error', res.text)
                QMessageBox.warning(self, "Acțiune blocată", error_msg)
        except Exception as e:
            QMessageBox.critical(self, "Eroare", str(e))