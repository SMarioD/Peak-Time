import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QMessageBox, QPushButton, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class StatisticsWindow(QWidget):
    def __init__(self, jwt_token, current_user_id, parent=None):
        super().__init__(parent)
        self.jwt_token = jwt_token
        self.current_user_id = current_user_id

        self.setWindowTitle("Statistici Performanță Echipă")
        self.setGeometry(300, 300, 800, 450)
        self.initUI()
        self.load_statistics()

    def initUI(self):
        layout = QVBoxLayout()

        title_label = QLabel("Indicatori de Performanță și Încărcare (KPIs)")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #007ACC; margin-bottom: 10px;")
        layout.addWidget(title_label)

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels([
            "Membru Echipă", "Sarcini Active", "Sarcini Finalizate", "Timp Mediu (ore)"
        ])

        header = self.stats_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)

        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #323232;
                gridline-color: #444;
                color: white;
                border: 1px solid #444;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #007ACC;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #2b2b2b;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #005A9E;
            }
        """)

        layout.addWidget(self.stats_table)

        self.refresh_button = QPushButton("🔄 Reîmprospătează Datele")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #008ae6;
            }
        """)
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
                self.stats_table.setSpan(0, 0, 1, 4)
                self.stats_table.setItem(0, 0, QTableWidgetItem("Niciun membru conectat în echipă."))
                return

            partner_ids = [conn.get('utilizator1Id') if conn.get('utilizator2Id') == self.current_user_id else conn.get(
                'utilizator2Id') for conn in connections]

            ids_string = ",".join(map(str, partner_ids))
            stats_url = f"http://localhost:8080/api/v1/statistics/team-performance?employeeIds={ids_string}"

            stats_response = requests.get(stats_url, headers=headers)

            if stats_response.status_code != 200:
                QMessageBox.critical(self, "Eroare", "Eroare la preluarea statisticilor de la server.")
                return

            stats_data = stats_response.json()
            stats_map = {stat['employeeId']: stat for stat in stats_data}
            details_map = self.fetch_user_details(partner_ids, headers)

            self.stats_table.setRowCount(len(partner_ids))
            for i, user_id in enumerate(partner_ids):
                user_email = details_map.get(user_id, f"ID: {user_id}")
                user_stats = stats_map.get(user_id)

                email_item = QTableWidgetItem(user_email)
                email_item.setForeground(QColor("#007ACC"))
                self.stats_table.setItem(i, 0, email_item)

                active = str(user_stats.get('activeTasks', '0')) if user_stats else "0"
                active_item = QTableWidgetItem(active)
                active_item.setTextAlignment(Qt.AlignCenter)
                self.stats_table.setItem(i, 1, active_item)

                completed = str(user_stats.get('totalTasksCompleted', '0')) if user_stats else "0"
                completed_item = QTableWidgetItem(completed)
                completed_item.setTextAlignment(Qt.AlignCenter)
                self.stats_table.setItem(i, 2, completed_item)

                avg_hours = user_stats.get('averageCompletionHours', 0.0) if user_stats else 0.0
                avg_item = QTableWidgetItem(f"{avg_hours:.2f} h")
                avg_item.setTextAlignment(Qt.AlignCenter)
                avg_item.setForeground(QColor("#00ff00") if avg_hours > 0 else QColor("#888"))
                self.stats_table.setItem(i, 3, avg_item)


        except Exception as e:
            QMessageBox.critical(self, "Eroare de Conexiune", f"Detaliu: {str(e)}")

    def fetch_user_details(self, user_ids, headers):
        if not user_ids: return {}
        details_url = "http://localhost:8080/api/v1/auth/users/details"
        try:
            response = requests.post(details_url, headers=headers, json=user_ids)
            if response.status_code == 200:
                return {
                    user['id']: f"{user.get('prenume', '')} {user.get('nume', '')}".strip() or user.get('email')
                    for user in response.json()
                }
        except:
            pass
        return {}