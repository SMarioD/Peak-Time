import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox


class CreateTeamDialog(QDialog):
    def __init__(self, token, parent=None):
        super().__init__(parent)
        self.token = token
        self.setWindowTitle("Creează Echipă Nouă")
        self.setFixedWidth(400)
        self.initUI()
        self.load_projects()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Nume Echipă:"))
        layout.addWidget(self.name_input)

        self.project_combo = QComboBox()
        layout.addWidget(QLabel("Selectează Proiectul:"))
        layout.addWidget(self.project_combo)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def load_projects(self):
        url = "http://localhost:8080/api/v1/teams/projects"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                for p in res.json():
                    self.project_combo.addItem(p['nume'], userData=p['id'])
            else:
                self.project_combo.addItem("Eroare încărcare proiecte", userData=None)
        except:
            self.project_combo.addItem("Eroare conexiune server", userData=None)

    def get_data(self):
        return {
            "nume": self.name_input.text(),
            "projectId": self.project_combo.currentData()
        }