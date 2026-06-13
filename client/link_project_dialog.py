import requests
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox, QMessageBox


class LinkProjectDialog(QDialog):
    def __init__(self, token, parent=None):
        super().__init__(parent)
        self.token = token
        self.setWindowTitle("🔗 Alocă Proiect Nou Echipei")
        self.setFixedWidth(400)
        self.initUI()
        self.load_projects()

    def initUI(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<b>Selectați proiectul de adăugat în portofoliul echipei:</b>"))
        self.project_combo = QComboBox()
        self.project_combo.setStyleSheet("padding: 5px;")
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
                    self.project_combo.addItem(f"🚀 {p['nume']}", userData=p['id'])
        except:
            pass

    def get_selected_project_id(self):
        return self.project_combo.currentData()