import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QPushButton, \
    QHeaderView


class StatisticsWindow(QWidget):
    def __init__(self, jwt_token, current_user_id, parent=None):
        super().__init__(parent)
        self.jwt_token = jwt_token
        self.current_user_id = current_user_id

        self.setWindowTitle("Statistici Echipă")
        self.setGeometry(300, 300, 700, 400)
        self.initUI()
        self.load_statistics()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Performanța și Încărcarea Membrilor Echipei:"))

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels([
            "Angajat", "Sarcini Active", "Sarcini Finalizate", "Timp Mediu Finalizare (ore)"
        ])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.stats_table)

        self.refresh_button = QPushButton("Reîmprospătează")
        self.refresh_button.clicked.connect(self.load_statistics)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

    def load_statistics(self):
        connections_url = "http://localhost:8080/api/v1/auth/connections"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(connections_url, headers=headers)
            if response.status_code != 200:
                QMessageBox.critical(self, "Eroare", "Nu s-au putut încărca membrii echipei.")
                return

            connections = [c for c in response.json() if c.get('status') == 'acceptat']
            if not connections:
                self.stats_table.setRowCount(1)
                self.stats_table.setItem(0, 0, QTableWidgetItem("Nu aveți membri în echipă."))
                return

            partner_ids = [conn.get('utilizator1Id') if conn.get('utilizator2Id') == self.current_user_id else conn.get(
                'utilizator2Id') for conn in connections]

            if not partner_ids:
                self.stats_table.setRowCount(1)
                self.stats_table.setItem(0, 0, QTableWidgetItem("Nu aveți membri în echipă."))
                return
            ids_string = ",".join(map(str, partner_ids))
            stats_url = f"http://localhost:8080/api/v1/statistics/team-performance?employeeIds={ids_string}"

            stats_response = requests.get(stats_url, headers=headers)

            if stats_response.status_code != 200:
                QMessageBox.critical(self, "Eroare", f"Nu s-au putut încărca statisticile: {stats_response.text}")
                return

            stats_data = stats_response.json()
            stats_map = {stat['employeeId']: stat for stat in stats_data}
            details_map = self.fetch_user_details(partner_ids, headers)
            self.stats_table.setRowCount(len(partner_ids))
            for i, user_id in enumerate(partner_ids):
                user_email = details_map.get(user_id, f"ID: {user_id}")
                user_stats = stats_map.get(user_id)

                self.stats_table.setItem(i, 0, QTableWidgetItem(user_email))
                if user_stats:
                    self.stats_table.setItem(i, 1, QTableWidgetItem(str(user_stats.get('activeTasks', '0'))))
                    self.stats_table.setItem(i, 2, QTableWidgetItem(str(user_stats.get('totalTasksCompleted', '0'))))
                    avg_hours = user_stats.get('averageCompletionHours', 0.0)
                    self.stats_table.setItem(i, 3, QTableWidgetItem(f"{avg_hours:.2f}"))
                else:
                    self.stats_table.setItem(i, 1, QTableWidgetItem("0"))
                    self.stats_table.setItem(i, 2, QTableWidgetItem("0"))
                    self.stats_table.setItem(i, 3, QTableWidgetItem("0.00"))

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def fetch_user_details(self, user_ids, headers):
        if not user_ids: return {}
        details_url = "http://localhost:8080/api/v1/auth/users/details"
        try:
            response = requests.post(details_url, headers=headers, json=user_ids)
            if response.status_code == 200:
                return {user['id']: user.get('email', 'N/A') for user in response.json()}
        except requests.exceptions.RequestException:
            pass
        return {}