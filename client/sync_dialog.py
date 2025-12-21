import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget, QDialogButtonBox,
                             QListWidgetItem, QMessageBox, QDateTimeEdit, QSpinBox)
from PyQt5.QtCore import Qt, QDateTime


class SyncDialog(QDialog):
    def __init__(self, jwt_token, current_user_id, parent=None):
        super().__init__(parent)
        self.jwt_token = jwt_token
        self.current_user_id = current_user_id

        self.setWindowTitle("Sincronizează Calendare")
        self.setGeometry(200, 200, 400, 500)
        self.initUI()
        self.load_connections()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Selectează utilizatorii pentru sincronizare (Ctrl+Click):"))
        self.connections_list = QListWidget()
        self.connections_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.connections_list)

        layout.addWidget(QLabel("Interval de căutare - De la:"))
        self.start_datetime = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_datetime.setCalendarPopup(True)
        layout.addWidget(self.start_datetime)

        layout.addWidget(QLabel("Până la:"))
        self.end_datetime = QDateTimeEdit(QDateTime.currentDateTime().addDays(1))
        self.end_datetime.setCalendarPopup(True)
        layout.addWidget(self.end_datetime)

        layout.addWidget(QLabel("Durata minimă a intervalului liber (minute):"))
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(15, 480)
        self.duration_spinbox.setValue(60)
        layout.addWidget(self.duration_spinbox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def load_connections(self):
        connections_url = "http://localhost:8080/api/v1/auth/connections"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(connections_url, headers=headers)
            if response.status_code == 200:
                connections = [c for c in response.json() if c.get('status') == 'acceptat']
                if not connections:
                    self.connections_list.addItem("Nicio conexiune acceptată.")
                    return

                partner_ids = {
                    conn.get('utilizator1Id') if conn.get('utilizator2Id') == self.current_user_id else conn.get(
                        'utilizator2Id') for conn in connections}

                if partner_ids:
                    details_url = "http://localhost:8080/api/v1/auth/users/details"
                    details_response = requests.post(details_url, headers=headers, json=list(partner_ids))
                    if details_response.status_code == 200:
                        for user in details_response.json():
                            item = QListWidgetItem(user.get('email'))
                            item.setData(Qt.UserRole, user)
                            self.connections_list.addItem(item)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def get_data(self):
        selected_items = self.connections_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Eroare", "Trebuie să selectezi cel puțin un utilizator.")
            return None

        user_ids = [self.current_user_id]
        for item in selected_items:
            user_ids.append(item.data(Qt.UserRole)['id'])

        return {
            "userIds": user_ids,
            "startDate": self.start_datetime.dateTime().toString(Qt.ISODate),
            "endDate": self.end_datetime.dateTime().toString(Qt.ISODate),
            "minDurationMinutes": self.duration_spinbox.value()
        }