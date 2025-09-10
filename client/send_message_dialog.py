import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QListWidget,
                             QPushButton, QMessageBox, QListWidgetItem)
from PyQt5.QtCore import Qt


class SendMessageDialog(QDialog):
    def __init__(self, jwt_token, current_user_id, parent=None):
        super().__init__(parent)
        self.jwt_token = jwt_token
        self.current_user_id = current_user_id
        self.selected_user = None

        self.setWindowTitle("Trimite Mesaj Nou")
        self.setGeometry(200, 200, 400, 500)
        self.initUI()
        self.load_connections()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Caută utilizator după email:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("email@exemplu.com")
        layout.addWidget(self.search_input)

        self.search_button = QPushButton("Caută")
        self.search_button.clicked.connect(self.search_user)
        layout.addWidget(self.search_button)

        layout.addWidget(QLabel("Sau selectează din conexiunile tale:"))
        self.user_list_widget = QListWidget()
        self.user_list_widget.itemDoubleClicked.connect(self.on_user_selected)
        layout.addWidget(self.user_list_widget)

        self.open_chat_button = QPushButton("Deschide Chat")
        self.open_chat_button.clicked.connect(self.on_user_selected)
        layout.addWidget(self.open_chat_button)

        self.setLayout(layout)

    def load_connections(self):
        connections_url = "http://localhost:8080/api/v1/auth/connections"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}

        try:
            response = requests.get(connections_url, headers=headers)
            if response.status_code == 200:
                connections = [c for c in response.json() if c.get('status') == 'acceptat']
                self.populate_user_list(connections)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def populate_user_list(self, connections):
        self.user_list_widget.clear()
        if not connections:
            self.user_list_widget.addItem("Nicio conexiune acceptată.")
            return

        partner_ids = {
            conn.get('utilizator1Id') if conn.get('utilizator2Id') == self.current_user_id else conn.get(
                'utilizator2Id')
            for conn in connections
        }

        if partner_ids:
            details_url = "http://localhost:8080/api/v1/auth/users/details"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            details_response = requests.post(details_url, headers=headers, json=list(partner_ids))
            if details_response.status_code == 200:
                for user in details_response.json():
                    list_item = QListWidgetItem(user.get('email'))
                    list_item.setData(Qt.UserRole, user)
                    self.user_list_widget.addItem(list_item)

    def search_user(self):
        email_to_search = self.search_input.text()
        if not email_to_search:
            QMessageBox.warning(self, "Atenție", "Introduceți un email pentru a căuta.")
            return

        search_url = f"http://localhost:8080/api/v1/auth/users/search?email={email_to_search}"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}

        try:
            response = requests.get(search_url, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                self.user_list_widget.clear()
                list_item = QListWidgetItem(user_data.get('email'))
                list_item.setData(Qt.UserRole, user_data)
                self.user_list_widget.addItem(list_item)
            else:
                QMessageBox.information(self, "Rezultat", "Niciun utilizator găsit cu acest email.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def on_user_selected(self):
        selected_items = self.user_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Atenție", "Vă rugăm selectați un utilizator din listă.")
            return

        self.selected_user = selected_items[0].data(Qt.UserRole)
        self.accept()

    def get_selected_user(self):
        return self.selected_user