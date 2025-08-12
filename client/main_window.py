from socket import create_connection
import requests
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QHBoxLayout, QVBoxLayout, QPushButton, QCalendarWidget, QMenu, \
    QDialog
from PyQt5.QtCore import Qt
from datetime import datetime
from new_event_dialog import NewEventDialog


class MainWindow(QWidget):
    def __init__(self, jwt_token):
        super().__init__()
        self.jwt_token = jwt_token
        self.events_data = []
        self.setWindowTitle("Peak Time - Panou Principal")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.load_calendar_events()

    def initUI(self):
        main_layout = QHBoxLayout()

        # --- ZONA STÂNGĂ ---
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)
        main_layout.addLayout(left_layout)

        # --- ZONA CENTRALĂ ---
        center_layout = QVBoxLayout()
        self.calendar_widget = QCalendarWidget(self)
        self.calendar_widget.selectionChanged.connect(self.on_date_selected)
        center_layout.addWidget(self.calendar_widget)

        self.daily_events_label = QLabel("Selecteaza o data pentru a vedea evenimentele.")
        self.daily_events_label.setAlignment(Qt.AlignTop)
        center_layout.addWidget(self.daily_events_label)
        main_layout.addLayout(center_layout, stretch=1)

        # --- ZONA DREAPTĂ ---
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)
        self.menu_button = QPushButton("☰", self)
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.clicked.connect(self.show_menu)
        right_layout.addWidget(self.menu_button)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    def on_date_selected(self):
        selected_date_qdate = self.calendar_widget.selectedDate()
        selected_date_str = selected_date_qdate.toString('yyyy-MM-dd')

        events_for_day = [
            event for event in self.events_data
            if event.get('dataInceput', '')[:10] == selected_date_str
        ]

        display_text = f"Evenimente pentru {selected_date_qdate.toString('dd-MM-yyyy')}:\n"
        if not events_for_day:
            display_text += "- Niciun eveniment"
        else:
            for event in events_for_day:
                try:
                    start_dt_obj = datetime.fromisoformat(event.get('dataInceput'))
                    end_dt_obj = datetime.fromisoformat(event.get('dataSfarsit'))

                    start_time = start_dt_obj.strftime('%H:%M')
                    end_time = end_dt_obj.strftime('%H:%M')

                    display_text += f"- {event.get('titlu')} ({start_time} - {end_time})\n"
                except (TypeError, ValueError) as e:
                    print(f"Eroare la parsarea datei pentru eveniment: {event}. Eroare: {e}")
                    display_text += f"- {event.get('titlu')} (ora invalida)\n"

        self.daily_events_label.setText(display_text)

    def show_menu(self):
        context_menu=QMenu(self)

        add_event_action = context_menu.addAction("Adaugă Eveniment")
        create_connection_action=context_menu.addAction("Creaza conexiune")
        sync_calendar_action = context_menu.addAction("Sincronizează calendarul")
        share_plans_action = context_menu.addAction("Partajează planuri")
        send_message_action = context_menu.addAction("Trimite mesaj")

        context_menu.addSeparator()
        logout_action=context_menu.addAction("Logout")

        point=self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft())
        selected_action = context_menu.exec_(point)

        #TODO: Adauga logica pentru fiecare
        if selected_action == add_event_action:
            self.handle_add_event()
        elif selected_action == logout_action:
            print("Utilizatorul dorește să se delogheze.")

    def handle_add_event(self):
        selected_date = self.calendar_widget.selectedDate()
        dialog = NewEventDialog(selected_date, self)
        if dialog.exec_() == QDialog.Accepted:
            event_data = dialog.get_data()
            if not event_data.get("titlu"):
                QMessageBox.warning(self, "Eroare", "Titlul evenimentului este obligatoriu.")
                return
            events_url = "http://localhost:8080/api/v1/calendar/events"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}

            try:
                response = requests.post(events_url, headers=headers, json=event_data)
                if response.status_code == 201:
                    QMessageBox.information(self, "Succes", "Evenimentul a fost adăugat.")
                    self.load_calendar_events()
                else:
                    QMessageBox.critical(self, "Eroare", f"Nu s-a putut adăuga evenimentul: {response.text}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def load_calendar_events(self):
        print("Încercare de a încărca evenimentele din calendar...")

        events_url = "http://localhost:8080/api/v1/calendar/events"

        headers={
            "Authorization": f"Bearer {self.jwt_token}"
        }

        try:
            response = requests.get(events_url, headers=headers)
            if response.status_code == 200:
                self.events_data = response.json()
                print(f"Au fost încărcate {len(self.events_data)} evenimente.")
                self.on_date_selected()
            else:
                QMessageBox.critical(self, "Eroare", "Nu s-au putut încărca evenimentele.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))