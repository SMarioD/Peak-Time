from socket import create_connection

from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QHBoxLayout, QVBoxLayout, QPushButton, QCalendarWidget, QMenu
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
import requests

class MainWindow(QWidget):
    def __init__(self,jwt_token):
        super().__init__()
        self.jwt_token=jwt_token
        self.events_data = []
        self.setWindowTitle("Peak TIme - Panou principal")
        self.setGeometry(100,100,800,600)
        self.initUI()
        self.load_calendar_events()


    def initUI(self):
        main_layout = QHBoxLayout()

        left_layout=QHBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)

        main_layout.addLayout(left_layout)

        center_layout=QVBoxLayout()

        self.calendar_widget=QCalendarWidget(self)
        self.calendar_widget.selectionChanged.connect(self.on_date_selected)
        center_layout.addWidget(self.calendar_widget)

        self.daily_event_label=QLabel("Selecteaza o data pentru a vedea evenimentele.")
        self.daily_event_label.setAlignment(Qt.AlignTop)
        center_layout.addWidget(self.daily_event_label)

        main_layout.addLayout(center_layout,stretch=1)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        self.menu_button = QPushButton("☰", self)
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.clicked.connect(self.show_menu)
        right_layout.addWidget(self.menu_button)
        main_layout.addLayout(right_layout)


        self.setLayout(main_layout)


    def on_date_selected(self):
        selected_date=self.calendar_widget.selectedDate()
        #TODO filtrare si afisare evenimente pentru data selectata
        self.daily_event_label.setText(f"Evenimente pentru {selected_date.toString('dd-MM-yyyy')}:\n- Niciun eveniment")
        print(f"Data selectată: {selected_date.toString('yyyy-MM-dd')}")

    def show_menu(self):
        context_menu=QMenu(self)

        create_connection_action=context_menu.addAction("Creaza conexiune")
        sync_calendar_action = context_menu.addAction("Sincronizează calendarul")
        share_plans_action = context_menu.addAction("Partajează planuri")
        send_message_action = context_menu.addAction("Trimite mesaj")

        #TODO Adauga actiunile specifice rolurilor( Manage Tasks, Manage Team)

        context_menu.addSeparator()
        logout_action=context_menu.addAction("Logout")

        point=self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft())
        selected_action=context_menu.exec_(point)

        #TODO: Adauga logica pentru fiecare

        if selected_action==logout_action:
            print("Utilizatorul doreste sa se delogheze.")
            #TODO Implementam logica de logut

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