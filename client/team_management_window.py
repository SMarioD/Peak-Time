import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QListWidget, QPushButton,
                             QLineEdit, QTextEdit, QListWidgetItem)
from PyQt5.QtCore import Qt

class TeamManagementWindow(QWidget):
    def __init__(self,jwt_token,user_id):
        super().__init__()
        self.jwt_token=jwt_token
        self.team_leader_id=user_id
        self.setWindowTitle("Management Echipa")
        self.setGeometry(200,200,700,500)
        self.initUI()
        self.load_team_members()

    def initUI(self):
        main_layout=QHBoxLayout()

        # --- Panoul Stanga: Membrii Echipei ---
        left_layout=QVBoxLayout()
        left_layout.addWidget(QLabel("Membrii Echipei:"))
        self.team_list_widget=QListWidget()
        left_layout.addWidget(self.team_list_widget)

        # --- Panoul Dreapta: Creare Task Nou ---
        right_layout=QVBoxLayout()
        right_layout.addWidget(QLabel("Creează o Sarcină Nouă"))

        self.title_lable=QLabel("Titlu Sarcina:")
        self.title_input=QLineEdit()
        right_layout.addWidget(self.title_lable)
        right_layout.addWidget(self.title_input)

        self.desc_label=QLabel("Descriere:")
        self.desc_input=QTextEdit()
        right_layout.addWidget(self.desc_label)
        right_layout.addWidget(self.desc_input)

        self.assign_button = QPushButton("Atribuie Sarcina")
        self.assign_button.clicked.connect(self.assign_task)
        right_layout.addWidget(self.assign_button)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)

        self.setLayout(main_layout)

    def load_team_members(self):
        # TODO: Aici adaugam logica pentru a prelua membrii echipei
        connections_url = "http://localhost:8080/api/v1/auth/connections"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}

        try:
            response = requests.get(connections_url, headers=headers)
            if response.status_code == 200:
                connections = response.json()
                accepted_connections = [c for c in connections if c.get('status') == 'acceptat']
                self.team_list_widget.clear()
                if not accepted_connections:
                    self.team_list_widget.addItem("Nu aveți membri în echipă.")
                    return

                partner_ids = {
                    conn.get('utilizator1Id') if conn.get('utilizator2Id') == self.team_leader_id else conn.get(
                        'utilizator2Id')
                    for conn in accepted_connections
                }

                if partner_ids:
                    details_url = "http://localhost:8080/api/v1/auth/users/details"
                    details_response = requests.post(details_url, headers=headers, json=list(partner_ids))
                    if details_response.status_code == 200:
                        for user in details_response.json():
                            list_item = QListWidgetItem(user.get('email'))
                            list_item.setData(Qt.UserRole, user)
                            self.team_list_widget.addItem(list_item)
            else:
                QMessageBox.critical(self, "Eroare", "Nu s-au putut încărca membrii echipei.")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def assign_task(self):
        selected_items = self.team_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Atenție", "Vă rugăm selectați un membru al echipei.")
            return

        selected_user = selected_items[0].data(Qt.UserRole)
        assignee_id = selected_user.get('id')
        task_title = self.title_input.text()
        task_description = self.desc_input.toPlainText()

        if not task_title:
            QMessageBox.warning(self, "Atenție", "Titlul sarcinii este obligatoriu.")
            return

        tasks_url = "http://localhost:8080/api/v1/tasks"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        payload = {
            "atribuitLuiId": assignee_id,
            "titlu": task_title,
            "descriere": task_description
        }

        try:
            response = requests.post(tasks_url, headers=headers, json=payload)
            if response.status_code == 201:
                QMessageBox.information(self, "Succes", f"Sarcina '{task_title}' a fost atribuită cu succes.")
                # Resetăm câmpurile
                self.title_input.clear()
                self.desc_input.clear()
            else:
                QMessageBox.critical(self, "Eroare", f"Nu s-a putut crea sarcina: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))
