from http.client import responses

import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QMessageBox, QPushButton)
from PyQt5.QtCore import Qt
from shared_plan_details_window import SharedPlanDetailsWindow

class SharedPlansWindow(QWidget):
    def __init__(self, jwt_token, current_user_id, parent=None):
        super().__init__(parent)
        self.jwt_token = jwt_token
        self.current_user_id = current_user_id
        self.details_window = None

        self.setWindowTitle("Calendare Partajate Cu Mine")
        self.setGeometry(250, 250, 500, 400)
        self.initUI()
        self.load_shared_plans()

    def initUI(self):
        layout=QVBoxLayout()
        layout.addWidget(QLabel("Selectează un calendar parajat pentru a vedea detaliile"))

        self.plans_list_widget=QListWidget()
        self.plans_list_widget.itemDoubleClicked.connect(self.on_plan_selected)
        layout.addWidget(self.plans_list_widget)

        self.refresh_button=QPushButton("Reîmprospătează")
        self.refresh_button.clicked.connect(self.load_shared_plans)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

    def load_shared_plans(self):
        self.plans_list_widget.clear()
        shares_url="http://localhost:8080/api/v1/calendar/shares"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}

        try:
            response=requests.get(shares_url,headers=headers)
            if response.status_code !=200:
                self.plans_list_widget.addItem("Eroare la încărcarea partajărilor.")
                return
            shares=response.json()
            if not shares:
                self.plans_list_widget.addItem("Nu a fost partajat niciun calendar cu tine.")
                return

            owner_ids={share['ownerUserId'] for share in shares}
            user_details_map=self.fetch_user_details(list(owner_ids))
            for share in shares:
                owner_email=user_details_map.get(share['ownerUserId'],"Utilizator Necunoscut")
                start_date=share['startDate'][:10]
                end_date=share['endDate'][:10]
                item_text=f"De la:{owner_email} (Perioada: {start_date} -> {end_date})"
                list_item=QListWidgetItem(item_text)
                list_item.setData(Qt.UserRole,share)
                self.plans_list_widget.addItem(list_item)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self,"Eroare de Conexiune", str(e))
            self.plans_list_widget.addItem("Eroare de conexiune.")

    def fetch_user_details(self,user_ids):
        if not user_ids:
            return {}
        details_url = "http://localhost:8080/api/v1/auth/users/details"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.post(details_url, headers=headers, json=user_ids)
            if response.status_code == 200:
                return {user['id']: user.get('email', 'Email Necunoscut') for user in response.json()}
        except requests.exceptions.RequestException as e:
            print(f"Nu s-au putut prelua detaliile utilizatorilor: {e}")
        return {}

    def on_plan_selected(self, item):
        share_data = item.data(Qt.UserRole)
        if not share_data:
            return

        self.details_window = SharedPlanDetailsWindow(self.jwt_token, share_data)
        self.details_window.show()