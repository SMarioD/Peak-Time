import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QListWidget, QPushButton,
                             QLineEdit, QTextEdit, QListWidgetItem, QDoubleSpinBox, QComboBox, QFormLayout)
from PyQt5.QtCore import Qt

from theme import SuccessDialog


class TeamManagementWindow(QWidget):
    def __init__(self,jwt_token,user_id):
        super().__init__()
        self.jwt_token = jwt_token
        self.team_leader_id = user_id
        self.existing_tasks = []
        self.setWindowTitle("Management Echipă - Planificare Avansată")
        self.setGeometry(200, 200, 900, 600)
        self.initUI()
        self.load_team_members()
        self.fetch_existing_tasks()

    def initUI(self):
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>Membrii Echipei:</b>"))
        self.team_list_widget = QListWidget()
        left_layout.addWidget(self.team_list_widget)
        main_layout.addLayout(left_layout, 1)

        right_layout = QVBoxLayout()
        form_container = QFormLayout()

        right_layout.addWidget(QLabel("<h2>Creează o Sarcină Nouă</h2>"))

        self.title_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        form_container.addRow("Titlu Sarcina:", self.title_input)
        form_container.addRow("Descriere:", self.desc_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["MICA", "MEDIE", "CRITICA"])
        self.priority_combo.setCurrentText("MEDIE")
        form_container.addRow("Prioritate:", self.priority_combo)

        self.predecessor_combo = QComboBox()
        self.predecessor_combo.addItem("Fără (Primul task)", None)
        form_container.addRow("Predecesor:", self.predecessor_combo)

        self.time_optimistic = QDoubleSpinBox()
        self.time_optimistic.setRange(0.1, 1000)
        self.time_optimistic.setSuffix(" ore")

        self.time_probable = QDoubleSpinBox()
        self.time_probable.setRange(0.1, 1000)
        self.time_probable.setSuffix(" ore")

        self.time_pessimistic = QDoubleSpinBox()
        self.time_pessimistic.setRange(0.1, 1000)
        self.time_pessimistic.setSuffix(" ore")

        form_container.addRow("Timp Optimist (O):", self.time_optimistic)
        form_container.addRow("Timp Probabil (P):", self.time_probable)
        form_container.addRow("Timp Pesimist (M):", self.time_pessimistic)

        right_layout.addLayout(form_container)

        self.assign_button = QPushButton("Atribuie Sarcina")
        self.assign_button.setStyleSheet("background-color: #007ACC; color: white; font-weight: bold; padding: 10px;")
        self.assign_button.clicked.connect(self.assign_task)
        right_layout.addWidget(self.assign_button)

        main_layout.addLayout(right_layout, 2)
        self.setLayout(main_layout)

    def fetch_existing_tasks(self):
        tasks_url = "http://localhost:8080/api/v1/tasks/created-by-me"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(tasks_url, headers=headers)
            if response.status_code == 200:
                self.existing_tasks = response.json()
                self.predecessor_combo.clear()
                self.predecessor_combo.addItem("Fără (Primul task)", None)
                for task in self.existing_tasks:
                    self.predecessor_combo.addItem(task['titlu'], task['id'])
        except:
            print("Eroare la preluarea predecesorilor.")

    def load_team_members(self):
        connections_url = "http://localhost:8080/api/v1/auth/connections"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(connections_url, headers=headers)
            if response.status_code == 200:
                accepted_connections = [c for c in response.json() if c.get('status') == 'acceptat']
                self.team_list_widget.clear()
                partner_ids = {conn.get('utilizator1Id') if conn.get('utilizator2Id') == self.team_leader_id else conn.get('utilizator2Id') for conn in accepted_connections}
                if partner_ids:
                    details_response = requests.post("http://localhost:8080/api/v1/auth/users/details", headers=headers, json=list(partner_ids))
                    if details_response.status_code == 200:
                        for user in details_response.json():
                            item = QListWidgetItem(user.get('email'))
                            item.setData(Qt.UserRole, user)
                            self.team_list_widget.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Eroare de conexiune: {str(e)}")

    def assign_task(self):
        selected_items = self.team_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Atenție", "Vă rugăm selectați un membru al echipei.")
            return

        assignee_id = selected_items[0].data(Qt.UserRole).get('id')
        payload = {
            "atribuitLuiId": assignee_id,
            "titlu": self.title_input.text(),
            "descriere": self.desc_input.toPlainText(),
            "prioritate": self.priority_combo.currentText(),
            "predecesorId": self.predecessor_combo.currentData(),
            "timpOptimist": self.time_optimistic.value(),
            "timpProbabil": self.time_probable.value(),
            "timpPesimist": self.time_pessimistic.value()
        }

        if not payload["titlu"]:
            QMessageBox.warning(self, "Atenție", "Titlul sarcinii este obligatoriu.")
            return

        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.post("http://localhost:8080/api/v1/tasks", headers=headers, json=payload)
            if response.status_code == 201:
                SuccessDialog(f"Sarcina '{payload['titlu']}' a fost creată cu durata estimată PERT.", self).exec_()
                self.title_input.clear()
                self.desc_input.clear()
                self.fetch_existing_tasks()
            else:
                QMessageBox.critical(self, "Eroare", f"Eroare: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))