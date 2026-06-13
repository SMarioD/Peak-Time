import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QLineEdit, QDialogButtonBox)
from PyQt5.QtCore import Qt


class ProjectSelectDialog(QDialog):
    def __init__(self, token, user_id, user_role, parent=None):
        super().__init__(parent)
        self.token = token
        self.user_id = user_id
        self.user_role = user_role
        self.setWindowTitle("🔍 Selectează Proiect pentru Gantt")
        self.resize(450, 500)
        self.setStyleSheet("background-color: #1A1927; color: #E2E8F0;")
        self.initUI()
        self.load_data()

    def initUI(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<b>Căutare Proiect:</b>"))
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Scrie numele proiectului...")
        self.search_bar.setStyleSheet("padding: 8px; background: #0F0E17; border: 1px solid #2D2B45;")
        self.search_bar.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_bar)

        self.project_list = QListWidget()
        self.project_list.setStyleSheet("background: #0F0E17; border-radius: 5px;")
        self.project_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.project_list)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def load_data(self):
        if self.user_role == 'team_leader':
            url = "http://localhost:8080/api/v1/teams/projects"
        else:
            url = "http://localhost:8080/api/v1/teams/my-projects"

        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                self.project_list.clear()
                for p in res.json():
                    item = QListWidgetItem(f"🚀 {p['nume']}")
                    item.setData(Qt.UserRole, p)
                    self.project_list.addItem(item)
        except:
            pass

    def filter_list(self, text):
        for i in range(self.project_list.count()):
            item = self.project_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def get_selected_project(self):
        item = self.project_list.currentItem()
        return item.data(Qt.UserRole) if item else None