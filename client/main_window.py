import requests
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QHBoxLayout, QVBoxLayout, QPushButton, QCalendarWidget, QMenu, QDialog, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from datetime import datetime
from new_event_dialog import NewEventDialog
from new_connection_dialog import NewConnectionDialog
from tasks_window import TasksWindow
from team_management_window import TeamManagementWindow
from chat_window import ChatWindow
from send_message_dialog import SendMessageDialog
from share_plan_dialog import SharePlanDialog
from shared_plans_window import SharedPlansWindow
from sync_dialog import SyncDialog
from statistics_window import StatisticsWindow


class MainWindow(QWidget):
    def __init__(self, jwt_token, user_id, user_role):
        super().__init__()
        self.jwt_token = jwt_token
        self.current_user_id = user_id
        self.current_user_role = user_role
        self.tasks_win = None
        self.team_management_win = None
        self.chat_windows = {}
        self.events_data = []
        self.sync_dialog = None
        self.statistics_win = None
        self.shared_plans_win = None
        self.setWindowTitle("Peak Time - Panou Principal")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.load_calendar_events()
        self.load_connections()

    def initUI(self):
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)
        main_layout.addLayout(left_layout)
        self.connections_list_widget = QListWidget()
        self.connections_list_widget.itemDoubleClicked.connect(self.on_connection_selected)
        left_layout.addWidget(QLabel("Conexiunile tale:"))
        left_layout.addWidget(self.connections_list_widget)
        self.refresh_connections_button = QPushButton("Reîmprospătează")
        self.refresh_connections_button.clicked.connect(self.load_connections)
        left_layout.addWidget(self.refresh_connections_button)

        center_layout = QVBoxLayout()
        self.calendar_widget = QCalendarWidget(self)
        self.calendar_widget.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.selectionChanged.connect(self.on_date_selected)
        center_layout.addWidget(self.calendar_widget)

        self.daily_events_label = QLabel("Selecteaza o data pentru a vedea evenimentele.")
        self.daily_events_label.setAlignment(Qt.AlignTop)
        center_layout.addWidget(self.daily_events_label)
        main_layout.addLayout(center_layout, stretch=1)

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

    def on_connection_selected(self, item):
        connection_data = item.data(Qt.UserRole)
        current_user_id = self.current_user_id

        if connection_data.get('status') == 'asteptare' and connection_data.get('utilizator2Id') == current_user_id:
            reply = QMessageBox.question(self, 'Cerere de Conexiune',
                                         f"Doriți să acceptați cererea de la acest utilizator?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if reply == QMessageBox.Yes: self.handle_update_connection(connection_data.get('id'), 'acceptat')
            elif reply == QMessageBox.No: self.handle_update_connection(connection_data.get('id'), 'respins')
        elif connection_data.get('status') == 'acceptat':
            partner_id = connection_data.get('utilizator1Id') if connection_data.get('utilizator2Id') == current_user_id else connection_data.get('utilizator2Id')
            if partner_id in self.chat_windows and self.chat_windows[partner_id].isVisible():
                self.chat_windows[partner_id].activateWindow()
                return
            details_url = "http://localhost:8080/api/v1/auth/users/details"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            try:
                details_response = requests.post(details_url, headers=headers, json=[partner_id])
                if details_response.status_code == 200:
                    partner_details = details_response.json()[0]
                    chat_win = ChatWindow(self.jwt_token, self.current_user_id, partner_details)
                    self.chat_windows[partner_id] = chat_win
                    chat_win.show()
                else:
                    QMessageBox.critical(self, "Eroare", "Nu s-au putut prelua detaliile partenerului.")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def show_menu(self):
        context_menu = QMenu(self)

        add_event_action = context_menu.addAction("Adaugă Eveniment")
        create_connection_action = context_menu.addAction("Crează conexiune")
        sync_calendar_action = context_menu.addAction("Sincronizează calendarul")
        share_plans_action = context_menu.addAction("Partajează planuri")
        send_message_action = context_menu.addAction("Trimite mesaj")
        view_shared_plans_action = context_menu.addAction("Calendare Partajate")

        manage_team_action, statistics_action, manage_tasks_action = None, None, None

        if self.current_user_role == 'team_leader':
            context_menu.addSeparator()
            manage_team_action = context_menu.addAction("Management Echipă")
            statistics_action = context_menu.addAction("Vezi Statistici")
        elif self.current_user_role == 'angajat':
            context_menu.addSeparator()
            manage_tasks_action = context_menu.addAction("Sarcinile Mele")

        context_menu.addSeparator()
        logout_action = context_menu.addAction("Logout")

        point = self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft())
        selected_action = context_menu.exec_(point)

        if selected_action:
            if selected_action == add_event_action: self.handle_add_event()
            elif selected_action == create_connection_action: self.handle_add_connection()
            elif selected_action == share_plans_action: self.handle_share_plan()
            elif selected_action == manage_team_action:
                self.team_management_win = TeamManagementWindow(self.jwt_token, self.current_user_id)
                self.team_management_win.show()
            elif selected_action == manage_tasks_action:
                self.tasks_win = TasksWindow(self.jwt_token, self.current_user_id)
                self.tasks_win.show()
            elif selected_action == sync_calendar_action: self.handle_sync_calendars()
            elif selected_action == statistics_action: self.handle_show_statistics()
            elif selected_action == view_shared_plans_action: self.handle_show_shared_plans()
            elif selected_action == send_message_action: self.handle_send_message()
            elif selected_action == logout_action: print("Utilizatorul dorește să se delogheze.")

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

    def handle_add_connection(self):
        dialog = NewConnectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            email = dialog.get_email()
            if not email:
                QMessageBox.warning(self, "Eroare", "Email-ul nu poate fi gol.")
                return
            connections_url = "http://localhost:8080/api/v1/auth/connections"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            payload = {"email": email}
            try:
                response = requests.post(connections_url, headers=headers, json=payload)
                if response.status_code == 200:
                    QMessageBox.information(self, "Succes", "Cererea de conexiune a fost trimisă.")
                    self.load_connections()
                else:
                    error_data = response.json()
                    QMessageBox.critical(self, "Eroare", error_data.get("error", "A apărut o eroare."))
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def handle_update_connection(self, connection_id, new_status):
        update_url = f"http://localhost:8080/api/v1/auth/connections/{connection_id}"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        payload = {"status": new_status}
        try:
            response = requests.put(update_url, headers=headers, json=payload)
            if response.status_code == 200:
                QMessageBox.information(self, "Succes", f"Cererea a fost marcată ca '{new_status}'.")
                self.load_connections()
            else:
                QMessageBox.critical(self, "Eroare", "Nu s-a putut actualiza statusul conexiunii.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def handle_send_message(self):
        dialog = SendMessageDialog(self.jwt_token, self.current_user_id, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_user = dialog.get_selected_user()
            if selected_user:
                partner_id = selected_user.get('id')
                if partner_id in self.chat_windows and self.chat_windows[partner_id].isVisible():
                    self.chat_windows[partner_id].activateWindow()
                    return
                chat_win = ChatWindow(self.jwt_token, self.current_user_id, selected_user)
                self.chat_windows[partner_id] = chat_win
                chat_win.show()

    def handle_share_plan(self):
        dialog = SharePlanDialog(self.jwt_token, self.current_user_id, self)
        if dialog.exec_() == QDialog.Accepted:
            payload = dialog.get_data()
            if not payload:
                QMessageBox.warning(self, "Eroare", "Trebuie să selectezi un utilizator.")
                return
            share_url = "http://localhost:8080/api/v1/share"
            headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
            try:
                response = requests.post(share_url, headers=headers, json=payload)
                if response.status_code == 200:
                    QMessageBox.information(self, "Succes", "Planul a fost partajat.")
                else:
                    QMessageBox.critical(self, "Eroare", f"Nu s-a putut partaja planul: {response.text}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def handle_show_shared_plans(self):
        self.shared_plans_win = SharedPlansWindow(self.jwt_token, self.current_user_id)
        self.shared_plans_win.show()

    def load_calendar_events(self):
        print("Încercare de a încărca evenimentele din calendar...")
        events_url = "http://localhost:8080/api/v1/calendar/events"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
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

    def load_connections(self):
        connections_url = "http://localhost:8080/api/v1/auth/connections"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(connections_url, headers=headers)
            if response.status_code != 200:
                self.connections_list_widget.clear()
                self.connections_list_widget.addItem("Eroare la încărcarea conexiunilor.")
                return
            connections = response.json()
            self.connections_list_widget.clear()
            if not connections:
                self.connections_list_widget.addItem("Nicio conexiune.")
                return
            current_user_id = self.current_user_id
            partner_ids = {conn.get('utilizator1Id') if conn.get('utilizator2Id') == current_user_id else conn.get('utilizator2Id') for conn in connections}
            user_details_map = {}
            if partner_ids:
                details_url = "http://localhost:8080/api/v1/auth/users/details"
                details_response = requests.post(details_url, headers=headers, json=list(partner_ids))
                if details_response.status_code == 200:
                    details_list = details_response.json()
                    user_details_map = {user.get('id'): user.get('email', 'Email necunoscut') for user in details_list}
                else:
                    print("Avertisment: Nu s-au putut prelua detaliile utilizatorilor.")
            for conn in connections:
                partner_id = conn.get('utilizator1Id') if conn.get('utilizator2Id') == current_user_id else conn.get('utilizator2Id')
                partner_email = user_details_map.get(partner_id, f"User ID: {partner_id}")
                item_text = f"{partner_email} ({conn.get('status')})"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.UserRole, conn)
                self.connections_list_widget.addItem(list_item)
        except requests.exceptions.RequestException as e:
            self.connections_list_widget.clear()
            self.connections_list_widget.addItem("Eroare de conexiune.")

    def handle_sync_calendars(self):
        self.sync_dialog = SyncDialog(self.jwt_token, self.current_user_id, self)
        if self.sync_dialog.exec_() == QDialog.Accepted:
            payload = self.sync_dialog.get_data()
            if not payload:
                return

            sync_url = "http://localhost:8080/api/v1/sync"
            headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}

            try:
                response = requests.post(sync_url, headers=headers, json=payload)
                if response.status_code == 200:
                    free_slots = response.json()
                    if not free_slots:
                        display_text = "Nu s-a găsit niciun interval liber comun care să respecte criteriile."
                    else:
                        display_text = "Intervale libere comune găsite:\n\n"
                        for slot in free_slots:
                            start_dt = datetime.fromisoformat(slot['startTime'])
                            end_dt = datetime.fromisoformat(slot['endTime'])
                            date_str = start_dt.strftime('%d %B %Y')
                            start_time_str = start_dt.strftime('%H:%M')
                            end_time_str = end_dt.strftime('%H:%M')

                            display_text += f"• În data de {date_str}, între orele {start_time_str} și {end_time_str}\n"

                    QMessageBox.information(self, "Rezultat Sincronizare", display_text)

                else:
                    QMessageBox.critical(self, "Eroare", f"Sincronizarea a eșuat: {response.text}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def handle_show_statistics(self):
        self.statistics_win = StatisticsWindow(self.jwt_token, self.current_user_id)
        self.statistics_win.show()