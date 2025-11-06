import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QMessageBox
from datetime import datetime


class SharedPlanDetailsWindow(QDialog):
    def __init__(self, jwt_token, share_data, parent=None):
        super().__init__(parent)
        self.jwt_token = jwt_token
        self.share_data = share_data

        self.setWindowTitle(f"Detalii Calendar Partajat")
        self.setGeometry(300, 300, 600, 400)
        self.initUI()
        self.load_shared_events()

    def initUI(self):
        layout = QVBoxLayout()
        self.details_label = QLabel("Se încarcă evenimentele...")
        layout.addWidget(self.details_label)

        self.events_list_widget = QListWidget()
        layout.addWidget(self.events_list_widget)

        self.setLayout(layout)

    def load_shared_events(self):
        owner_id = self.share_data.get('ownerUserId')
        events_url = f"http://localhost:8080/api/v1/calendar/events?userId={owner_id}"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}

        try:
            response = requests.get(events_url, headers=headers)
            if response.status_code != 200:
                QMessageBox.critical(self, "Eroare", "Nu s-au putut încărca evenimentele partajate.")
                return

            all_events = response.json()

            start_share_dt = datetime.fromisoformat(self.share_data['startDate'])
            end_share_dt = datetime.fromisoformat(self.share_data['endDate'])
            hidden_ids = self.share_data.get('hiddenEventIds')
            hidden_ids_list = [int(id_str) for id_str in hidden_ids.split(',') if id_str] if hidden_ids else []

            display_text = f"Evenimente partajate pentru perioada {start_share_dt.strftime('%Y-%m-%d')} - {end_share_dt.strftime('%Y-%m-%d')}:"
            self.details_label.setText(display_text)

            self.events_list_widget.clear()
            visible_events_found = False
            for event in all_events:
                event_start_dt = datetime.fromisoformat(event['dataInceput'])

                if start_share_dt <= event_start_dt < end_share_dt and event['id'] not in hidden_ids_list:
                    event_end_dt = datetime.fromisoformat(event['dataSfarsit'])
                    start_time = event_start_dt.strftime('%Y-%m-%d %H:%M')
                    end_time = event_end_dt.strftime('%H:%M')
                    self.events_list_widget.addItem(f"{event['titlu']} ({start_time} - {end_time})")
                    visible_events_found = True

            if not visible_events_found:
                self.events_list_widget.addItem("Niciun eveniment vizibil în acest interval.")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))