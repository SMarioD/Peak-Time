import requests
from PyQt5.QtWidgets import (QWidget, QLabel, QMessageBox, QHBoxLayout, QVBoxLayout,
                             QPushButton, QCalendarWidget, QMenu, QDialog, QListWidget,
                             QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer,QDate,QEvent
from PyQt5.QtGui import QColor, QPainter
from datetime import datetime

from google_sync_dialog import GoogleSyncDialog
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

class CustomCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_date = None
        self.current_date = None
        self.is_selecting = False
        self._drag_started = False
        self._drag_threshold = 5
        self._press_pos = None

        self.view = None
        from PyQt5.QtWidgets import QAbstractItemView
        views = self.findChildren(QAbstractItemView)
        if views:
            self.view = views[0]

        if self.view:
            self.view.viewport().installEventFilter(self)
            self.view.viewport().setMouseTracking(True)

        print(f"[DEBUG] View final: {self.view}")

        if self.view:
            self.view.installEventFilter(self)
            self.view.setMouseTracking(True)  # esențial pentru MouseMove!
        else:
            print("[EROARE] Nu s-a găsit view-ul calendarului!")

    def _date_at(self, pos):
        view = self.view
        if not view:
            return QDate()
        total_w = view.width()
        total_h = view.height()
        header_h = total_h // 7
        col = int(pos.x() / (total_w / 7))
        row = int((pos.y() - header_h) / ((total_h - header_h) / 6))
        col = max(0, min(6, col))
        row = max(0, min(5, row))
        first_visible = self._first_visible_date()
        if not first_visible.isValid():
            return QDate()
        return first_visible.addDays(row * 7 + col)

    def _first_visible_date(self):
        first_of_month = QDate(self.yearShown(), self.monthShown(), 1)
        day_of_week = first_of_month.dayOfWeek()
        first_dow = self.firstDayOfWeek()
        if first_dow == Qt.Sunday:
            col_of_first = day_of_week % 7
        else:
            col_of_first = (day_of_week - 1) % 7
        return first_of_month.addDays(-col_of_first)

    def eventFilter(self, obj, event):
        if obj == self.view.viewport():
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self._press_pos = event.pos()
                    self._drag_started = False
                    self.start_date = self._date_at(event.pos())
                    self.current_date = self.start_date
                    self.is_selecting = False
                    print(f"[PRESS] pos={event.pos()}, date={self.start_date}")

            elif event.type() == QEvent.MouseMove:
                if self._press_pos is not None:
                    delta = (event.pos() - self._press_pos)
                    dist = (delta.x() ** 2 + delta.y() ** 2) ** 0.5
                    print(f"[MOVE] dist={dist:.1f}, drag_started={self._drag_started}")
                    if dist >= self._drag_threshold:
                        self._drag_started = True
                        self.is_selecting = True
                        new_date = self._date_at(event.pos())
                        print(f"[DRAG] new_date={new_date}")
                        if new_date.isValid() and new_date != self.current_date:
                            self.current_date = new_date
                            self.update()

            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    print(f"[RELEASE] drag_started={self._drag_started}, start={self.start_date}")
                    if self._drag_started:
                        self.is_selecting = False
                        end_date = self._date_at(event.pos())
                        if (self.start_date and self.start_date.isValid()
                                and end_date.isValid()
                                and self.start_date != end_date):
                            d1 = self.start_date if self.start_date < end_date else end_date
                            d2 = end_date if self.start_date < end_date else self.start_date
                            main_win = self.window()
                            if hasattr(main_win, 'handle_add_event_range'):
                                main_win.handle_add_event_range(d1, d2)
                        self.start_date = None
                        self.current_date = None
                        self.update()
                    self._press_pos = None
                    self._drag_started = False

        return super().eventFilter(obj, event)

    def paintCell(self, painter, rect, date):
        if self.is_selecting and self.start_date and self.current_date:
            d1 = self.start_date if self.start_date < self.current_date else self.current_date
            d2 = self.current_date if self.start_date < self.current_date else self.start_date
            if d1 <= date <= d2:
                painter.save()
                painter.fillRect(rect, QColor("#007ACC"))
                painter.setPen(Qt.white)
                painter.drawText(rect, Qt.AlignCenter, str(date.day()))
                painter.restore()
                return
        super().paintCell(painter, rect, date)


class MainWindow(QWidget):
    def __init__(self, jwt_token, user_id, user_role):
        super().__init__()
        self.jwt_token = jwt_token
        self.current_user_id = user_id
        self.current_user_role = user_role

        self.tasks_win = None
        self.team_management_win = None
        self.statistics_win = None
        self.shared_plans_win = None
        self.chat_windows = {}
        self.events_data = []

        self.setWindowTitle("Peak Time - Panou Principal")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

        self.calendar_widget.activated.connect(self.on_calendar_activated)

        self.load_calendar_events()
        self.load_connections()

        # Timer Refresh Evenimente (1 minut)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_calendar_events)
        self.refresh_timer.start(60000)

        # Timer Refresh Conexiuni (30 secunde)
        self.connections_timer = QTimer(self)
        self.connections_timer.timeout.connect(self.load_connections)
        self.connections_timer.start(30000)

    def initUI(self):
        main_layout = QHBoxLayout()

        # --- Stânga: Conexiuni ---
        left_layout = QVBoxLayout()
        self.connections_list_widget = QListWidget()
        self.connections_list_widget.setMaximumWidth(180)
        self.connections_list_widget.itemDoubleClicked.connect(self.on_connection_selected)
        left_layout.addWidget(QLabel("Conexiunile tale:"))
        left_layout.addWidget(self.connections_list_widget)

        self.refresh_connections_button = QPushButton("Reîmprospătează")
        self.refresh_connections_button.setFixedWidth(180)
        self.refresh_connections_button.clicked.connect(self.load_connections)
        left_layout.addWidget(self.refresh_connections_button)
        main_layout.addLayout(left_layout, 1)

        # --- Centru: Calendar ---
        center_layout = QVBoxLayout()
        self.calendar_widget = CustomCalendar(self)
        self.calendar_widget.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.selectionChanged.connect(self.on_date_selected)

        center_layout.addWidget(self.calendar_widget, stretch=1)

        self.daily_events_list = QListWidget()
        self.daily_events_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.daily_events_list.customContextMenuRequested.connect(self.show_context_menu)

        self.daily_events_list.setMaximumHeight(80)
        self.daily_events_list.setStyleSheet("background-color: transparent; border-top: 1px solid #444;")

        center_layout.addWidget(self.daily_events_list, stretch=0)
        main_layout.addLayout(center_layout, stretch=4)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)
        self.menu_button = QPushButton("☰", self)
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.clicked.connect(self.show_menu)
        right_layout.addWidget(self.menu_button)
        main_layout.addLayout(right_layout, 0)

        self.setLayout(main_layout)

    def on_calendar_activated(self, date):
        print(f"[ACTIVATED] date={date}, drag_started={self.calendar_widget._drag_started}")
        if not self.calendar_widget._drag_started:
            self.handle_add_event()

    def on_date_selected(self):
        selected_date_qdate = self.calendar_widget.selectedDate()
        selected_date_str = selected_date_qdate.toString('yyyy-MM-dd')
        selected_date_dt = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

        self.daily_events_list.clear()  # Curățăm lista veche

        found = False
        for event in self.events_data:
            try:
                start_dt = datetime.fromisoformat(event.get('dataInceput')).date()
                end_dt = datetime.fromisoformat(event.get('dataSfarsit')).date()

                if start_dt <= selected_date_dt <= end_dt:
                    st_time = event.get('dataInceput')[11:16]
                    en_time = event.get('dataSfarsit')[11:16]

                    item_text = f"{event.get('titlu')} ({st_time} - {en_time})"
                    list_item = QListWidgetItem(item_text)

                    list_item.setData(Qt.UserRole, event)
                    self.daily_events_list.addItem(list_item)
                    found = True
            except:
                continue

        if not found:
            self.daily_events_list.addItem("Niciun eveniment pentru această dată.")

    def show_context_menu(self, position):
        item = self.daily_events_list.itemAt(position)
        if not item or item.data(Qt.UserRole) is None:
            return

        menu = QMenu()
        delete_action = menu.addAction("Șterge Evenimentul")

        action = menu.exec_(self.daily_events_list.mapToGlobal(position))

        if action == delete_action:
            self.handle_delete_event(item)

    def handle_delete_event(self, item):
        event_data = item.data(Qt.UserRole)
        event_id = event_data.get('id')
        event_title = event_data.get('titlu')

        reply = QMessageBox.question(self, 'Confirmare Ștergere',
                                     f"Sigur doriți să ștergeți '{event_title}'?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            url = f"http://localhost:8080/api/v1/calendar/events/{event_id}"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            try:
                response = requests.delete(url, headers=headers)
                if response.status_code == 200:
                    QMessageBox.information(self, "Succes", "Evenimentul a fost șters.")
                    self.load_calendar_events()  # Reîncărcăm lista automat
                else:
                    QMessageBox.critical(self, "Eroare", f"Nu s-a putut șterge: {response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Eroare de conexiune", str(e))

    def handle_add_event(self):
        selected_date = self.calendar_widget.selectedDate()
        self.open_event_dialog(selected_date, selected_date)

    def handle_add_event_range(self, start_date, end_date):
        self.open_event_dialog(start_date, end_date)

    def open_event_dialog(self, start_date, end_date):
        dialog = NewEventDialog(start_date, end_date, self)
        if dialog.exec_() == QDialog.Accepted:
            event_data = dialog.get_data()
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            try:
                response = requests.post("http://localhost:8080/api/v1/calendar/events", headers=headers,
                                         json=event_data)
                if response.status_code == 201:
                    QMessageBox.information(self, "Succes", "Eveniment adăugat!")
                    self.load_calendar_events()
                else:
                    QMessageBox.critical(self, "Eroare", f"Eroare server: {response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Eroare", str(e))

    def load_connections(self):
        connections_url = "http://localhost:8080/api/v1/auth/connections"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(connections_url, headers=headers)
            if response.status_code == 200:
                connections = response.json()
                current_row = self.connections_list_widget.currentRow()
                self.connections_list_widget.clear()

                # Colectăm ID-urile partenerilor pentru a lua detaliile (email)
                partner_ids = {
                    conn.get('utilizator1Id') if conn.get('utilizator2Id') == self.current_user_id else conn.get(
                        'utilizator2Id') for conn in connections}
                user_details_map = {}
                if partner_ids:
                    details_url = "http://localhost:8080/api/v1/auth/users/details"
                    details_response = requests.post(details_url, headers=headers, json=list(partner_ids))
                    if details_response.status_code == 200:
                        user_details_map = {u.get('id'): u.get('email') for u in details_response.json()}

                for conn in connections:
                    p_id = conn.get('utilizator1Id') if conn.get('utilizator2Id') == self.current_user_id else conn.get(
                        'utilizator2Id')
                    email = user_details_map.get(p_id, f"User {p_id}")
                    status = conn.get('status')
                    display_status = "⌛" if status == "asteptare" else "✅"

                    item = QListWidgetItem(f"{email} {display_status}")
                    item.setData(Qt.UserRole, conn)
                    if status == 'asteptare' and conn.get('utilizator2Id') == self.current_user_id:
                        item.setBackground(Qt.yellow)
                    self.connections_list_widget.addItem(item)

                if current_row >= 0: self.connections_list_widget.setCurrentRow(current_row)
        except Exception as e:
            print(f"Eroare refresh conexiuni: {e}")

    def on_connection_selected(self, item):
        connection_data = item.data(Qt.UserRole)
        if connection_data.get('status') == 'asteptare' and connection_data.get(
                'utilizator2Id') == self.current_user_id:
            reply = QMessageBox.question(self, 'Cerere Conexiune', "Acceptați cererea?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.handle_update_connection(connection_data.get('id'), 'acceptat')
            elif reply == QMessageBox.No:
                self.handle_update_connection(connection_data.get('id'), 'respins')
        elif connection_data.get('status') == 'acceptat':
            p_id = connection_data.get('utilizator1Id') if connection_data.get(
                'utilizator2Id') == self.current_user_id else connection_data.get('utilizator2Id')
            # Deschidere Chat (logica ta existentă)
            pass

    def handle_update_connection(self, c_id, status):
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            requests.put(f"http://localhost:8080/api/v1/auth/connections/{c_id}", headers=headers,
                         json={"status": status})
            self.load_connections()
        except:
            pass

    def load_calendar_events(self):
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get("http://localhost:8080/api/v1/calendar/events", headers=headers)
            if response.status_code == 200:
                self.events_data = response.json()
                self.on_date_selected()
        except:
            pass

    def handle_logout(self):
        reply = QMessageBox.question(self, 'Logout', "Sigur doriți să vă delogați?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if hasattr(self, 'refresh_timer'): self.refresh_timer.stop()
            if hasattr(self, 'connections_timer'): self.connections_timer.stop()

            windows = ['tasks_win', 'team_management_win', 'statistics_win', 'shared_plans_win']
            for win_name in windows:
                win = getattr(self, win_name, None)
                if win and win.isVisible():
                    win.close()

            for chat_win in self.chat_windows.values():
                if chat_win.isVisible():
                    chat_win.close()
            from main import LoginWindow
            self.login_win = LoginWindow()
            self.login_win.show()
            self.close()

    def show_menu(self):
        context_menu = QMenu(self)

        add_event_action = context_menu.addAction("Adauga Eveniment")
        create_connection_action = context_menu.addAction("Creaza conexiune")
        sync_calendar_action = context_menu.addAction("Sincronizeaza calendarul")
        share_plans_action = context_menu.addAction("Partajeaza planuri")
        send_message_action = context_menu.addAction("Trimite mesaj")
        view_shared_plans_action = context_menu.addAction("Calendare Partajate")
        sync_google_action = context_menu.addAction("Sincronizeaza cu Google Calendar")

        manage_team_action, statistics_action, manage_tasks_action = None, None, None

        if self.current_user_role == 'team_leader':
            context_menu.addSeparator()
            manage_team_action = context_menu.addAction("Management Echipa")
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
            elif selected_action == sync_google_action:
                self.handle_sync_with_google()
            elif selected_action == sync_calendar_action: self.handle_sync_calendars()
            elif selected_action == statistics_action: self.handle_show_statistics()
            elif selected_action == view_shared_plans_action: self.handle_show_shared_plans()
            elif selected_action == send_message_action: self.handle_send_message()
            elif selected_action == logout_action:self.handle_logout()

    def handle_add_event(self):
        selected_date = self.calendar_widget.selectedDate()
        self.open_event_dialog(selected_date, selected_date)

    def handle_add_event_range(self, start_date, end_date):
        self.open_event_dialog(start_date, end_date)

    def open_event_dialog(self, start_date, end_date):
        dialog = NewEventDialog(start_date, end_date, self)
        if dialog.exec_() == QDialog.Accepted:
            event_data = dialog.get_data()
            if not event_data.get("titlu"):
                QMessageBox.warning(self, "Eroare", "Titlul este obligatoriu.")
                return

            events_url = "http://localhost:8080/api/v1/calendar/events"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            try:
                response = requests.post(events_url, headers=headers, json=event_data)
                if response.status_code == 201:
                    QMessageBox.information(self, "Succes", "Eveniment adăugat!")
                    self.load_calendar_events()
                else:
                    QMessageBox.critical(self, "Eroare", f"Eroare server: {response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Eroare", str(e))

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
                    QMessageBox.information(self, "Succes", "Cererea de conexiune a fost trimisa.")
                    self.load_connections()
                else:
                    error_data = response.json()
                    QMessageBox.critical(self, "Eroare", error_data.get("error", "A aparut o eroare."))
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def handle_update_connection(self, connection_id, new_status):
        update_url = f"http://localhost:8080/api/v1/auth/connections/{connection_id}"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        payload = {"status": new_status}
        try:
            response = requests.put(update_url, headers=headers, json=payload)
            if response.status_code == 200:
                QMessageBox.information(self, "Succes", f"Cererea a fost marcata ca '{new_status}'.")
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
                QMessageBox.warning(self, "Eroare", "Trebuie sa selectezi un utilizator.")
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
        print("incercare de a incarca evenimentele din calendar...")
        events_url = "http://localhost:8080/api/v1/calendar/events"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(events_url, headers=headers)
            if response.status_code == 200:
                self.events_data = response.json()
                print(f"Au fost incarcate {len(self.events_data)} evenimente.")
                self.on_date_selected()
            else:
                QMessageBox.critical(self, "Eroare", "Nu s-au putut incarca evenimentele.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def load_connections(self):
        connections_url = "http://localhost:8080/api/v1/auth/connections"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(connections_url, headers=headers)
            if response.status_code != 200:
                self.connections_list_widget.clear()
                self.connections_list_widget.addItem("Eroare la incarcarea conexiunilor.")
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

    def load_connections(self):
        connections_url = "http://localhost:8080/api/v1/auth/connections"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(connections_url, headers=headers)
            if response.status_code != 200:
                print(f"Avertisment: Nu s-au putut incarca conexiunile (Status {response.status_code})")
                return

            connections = response.json()
            current_row = self.connections_list_widget.currentRow()

            self.connections_list_widget.clear()
            if not connections:
                self.connections_list_widget.addItem("Nicio conexiune.")
                return

            current_user_id = self.current_user_id
            partner_ids = {
                conn.get('utilizator1Id') if conn.get('utilizator2Id') == current_user_id else conn.get('utilizator2Id')
                for conn in connections}

            user_details_map = {}
            if partner_ids:
                details_url = "http://localhost:8080/api/v1/auth/users/details"
                details_response = requests.post(details_url, headers=headers, json=list(partner_ids))
                if details_response.status_code == 200:
                    details_list = details_response.json()
                    user_details_map = {user.get('id'): user.get('email', 'Email necunoscut') for user in details_list}

            for conn in connections:
                partner_id = conn.get('utilizator1Id') if conn.get('utilizator2Id') == current_user_id else conn.get(
                    'utilizator2Id')
                partner_email = user_details_map.get(partner_id, f"User ID: {partner_id}")

                status = conn.get('status')
                display_status = "⌛ Cerere" if status == "asteptare" else "✅"

                item_text = f"{partner_email} {display_status}"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.UserRole, conn)

                if status == "asteptare" and conn.get('utilizator2Id') == current_user_id:
                    list_item.setBackground(Qt.yellow)
                    list_item.setForeground(Qt.black)

                self.connections_list_widget.addItem(list_item)
            if current_row >= 0:
                self.connections_list_widget.setCurrentRow(current_row)

        except requests.exceptions.RequestException as e:
            print(f"Eroare de conexiune la refresh-ul prietenilor: {e}")

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
                        display_text = "Nu s-a gasit niciun interval liber comun care sa respecte criteriile."
                    else:
                        display_text = "Intervale libere comune gasite:\n\n"
                        for slot in free_slots:
                            start_dt = datetime.fromisoformat(slot['startTime'])
                            end_dt = datetime.fromisoformat(slot['endTime'])
                            date_str = start_dt.strftime('%d %B %Y')
                            start_time_str = start_dt.strftime('%H:%M')
                            end_time_str = end_dt.strftime('%H:%M')

                            display_text += f"• in data de {date_str}, intre orele {start_time_str} si {end_time_str}\n"

                    QMessageBox.information(self, "Rezultat Sincronizare", display_text)

                else:
                    QMessageBox.critical(self, "Eroare", f"Sincronizarea a esuat: {response.text}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def handle_logout(self):
        reply = QMessageBox.question(self, 'Logout', "Sigur doriti sa va delogati?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if hasattr(self, 'refresh_timer'): self.refresh_timer.stop()
            if hasattr(self, 'connections_timer'): self.connections_timer.stop()
            windows_to_close = [self.tasks_win, self.team_management_win, self.statistics_win, self.shared_plans_win]
            for win in windows_to_close:
                if win and win.isVisible():
                    win.close()

            for chat_win in self.chat_windows.values():
                if chat_win.isVisible():
                    chat_win.close()
            from main import LoginWindow
            self.login_win = LoginWindow()
            self.login_win.show()
            self.close()

    def handle_show_statistics(self):
        self.statistics_win = StatisticsWindow(self.jwt_token, self.current_user_id)
        self.statistics_win.show()

    def handle_sync_with_google(self):
        self.google_sync_dialog = GoogleSyncDialog(self.jwt_token, self.current_user_id, self)
        self.google_sync_dialog.exec_()