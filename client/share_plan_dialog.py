import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, QDateTimeEdit, QListWidget, QDialogButtonBox, QListWidgetItem, QMessageBox)
from PyQt5.QtCore import QDateTime, Qt

class SharePlanDialog(QDialog):
    def __init__(self, jwt_token, current_user_id, parent=None):
        super().__init__(parent)
        self.all_user_events=[]
        self.jwt_token=jwt_token
        self.current_user_id=current_user_id
        self.connections= []
        self.events= []

        self.setWindowTitle("Partajeaza Planul")
        self.setGeometry(200,200,450,500)
        self.initUI()

        self.load_connections()
        self.load_all_events_from_api()

    def initUI(self):
        layout = QVBoxLayout()

        # Creăm widget-urile întâi
        layout.addWidget(QLabel("Partajeaza cu:"))
        self.connections_combo = QComboBox()
        layout.addWidget(self.connections_combo)

        layout.addWidget(QLabel("De la:"))
        self.start_datetime = QDateTimeEdit(QDateTime.currentDateTime())
        layout.addWidget(self.start_datetime)

        layout.addWidget(QLabel("Până la:"))
        self.end_datetime = QDateTimeEdit(QDateTime.currentDateTime().addDays(7))
        layout.addWidget(self.end_datetime)

        self.start_datetime.setCalendarPopup(True)
        self.end_datetime.setCalendarPopup(True)
        self.start_datetime.dateTimeChanged.connect(self.update_events_list)
        self.end_datetime.dateTimeChanged.connect(self.update_events_list)

        layout.addWidget(QLabel("Selectează evenimentele de ascuns (opțional):"))
        self.events_list = QListWidget()
        self.events_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.events_list)

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
            if response.status_code != 200:
                QMessageBox.critical(self, "Eroare", "Nu s-au putut încărca conexiunile.")
                return

            connections = [c for c in response.json() if c.get('status') == 'acceptat']
            if not connections:
                self.connections_combo.addItem("Nicio conexiune acceptată")
                return

            partner_ids = {
                conn.get('utilizator1Id') if conn.get('utilizator2Id') == self.current_user_id else conn.get(
                    'utilizator2Id')
                for conn in connections
            }

            if partner_ids:
                details_url = "http://localhost:8080/api/v1/auth/users/details"
                details_response = requests.post(details_url, headers=headers, json=list(partner_ids))
                if details_response.status_code == 200:
                    user_details = details_response.json()
                    for user in user_details:
                        self.connections_combo.addItem(user.get('email'), userData=user)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def load_events(self):
        events_url = "http://localhost:8080/api/v1/calendar/events"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(events_url, headers=headers)
            if response.status_code == 200:
                self.events = response.json()
                self.events_list.clear()
                if not self.events:
                    self.events_list.addItem("Nu aveți evenimente de ascuns.")
                else:
                    for event in self.events:
                        item_text = f"{event.get('titlu')} ({event.get('dataInceput')})"
                        list_item = QListWidgetItem(item_text)
                        list_item.setData(Qt.UserRole, event)
                        self.events_list.addItem(list_item)
            else:
                QMessageBox.critical(self, "Eroare", "Nu s-au putut încărca evenimentele.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def load_all_events_from_api(self):
        events_url = "http://localhost:8080/api/v1/calendar/events"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(events_url, headers=headers)
            if response.status_code == 200:
                self.all_user_events = response.json()
                self.update_events_list()
            else:
                QMessageBox.critical(self, "Eroare", "Nu s-au putut încărca evenimentele.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def update_events_list(self):
        self.events_list.clear()

        start_dt = self.start_datetime.dateTime()
        end_dt = self.end_datetime.dateTime()

        if start_dt >= end_dt:
            self.events_list.addItem("Intervalul de timp este invalid.")
            return

        filtered_events = []
        for event in self.all_user_events:
            try:
                event_start_dt = QDateTime.fromString(event.get('dataInceput'), Qt.ISODate)
                if start_dt <= event_start_dt < end_dt:
                    filtered_events.append(event)
            except Exception as e:
                print(f"Eroare la parsarea datei evenimentului: {e}")

        if not filtered_events:
            self.events_list.addItem("Niciun eveniment în acest interval.")
        else:
            for event in filtered_events:
                item_text = f"{event.get('titlu')} ({event.get('dataInceput')})"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.UserRole, event)
                self.events_list.addItem(list_item)

    def get_data(self):
        selected_connection_index = self.connections_combo.currentIndex()
        if selected_connection_index < 0:
            return None

        shared_with_user = self.connections_combo.itemData(selected_connection_index)
        if not shared_with_user:
            return None

        hidden_events_ids = []
        for item in self.events_list.selectedItems():
            hidden_events_ids.append(item.data(Qt.UserRole)['id'])

        return {
            "sharedWithUserId": shared_with_user['id'],
            "startDate": self.start_datetime.dateTime().toString(Qt.ISODate),
            "endDate": self.end_datetime.dateTime().toString(Qt.ISODate),
            "hiddenEventIds": hidden_events_ids
        }