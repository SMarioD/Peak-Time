import requests
from datetime import datetime

from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
                             QComboBox, QDoubleSpinBox, QDialogButtonBox, QMessageBox, QDateTimeEdit)


class AssignTaskDialog(QDialog):
    def __init__(self, team_id, project_id, token, parent=None):
        super().__init__(parent)
        self.team_id = team_id
        self.project_id = project_id
        self.token = token
        self.setWindowTitle("Atribuie Sarcină cu Planificare")
        self.setFixedWidth(400)
        self.initUI()
        self.load_members()
        self.load_existing_tasks()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.title_input = QLineEdit()
        layout.addWidget(QLabel("Titlu Sarcină:"))
        layout.addWidget(self.title_input)

        self.member_combo = QComboBox()
        layout.addWidget(QLabel("Atribuie membrului:"))
        layout.addWidget(self.member_combo)

        layout.addWidget(QLabel("<b>📅 Programare în timp:</b>"))
        self.start_date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_date_input.setCalendarPopup(True)
        layout.addWidget(QLabel("Data Început Estimată:"))
        layout.addWidget(self.start_date_input)

        layout.addWidget(QLabel("<b>🔗 Dependență (Predecesor):</b>"))
        self.predecessor_combo = QComboBox()
        self.predecessor_combo.addItem("Fără (Începe independent)", None)
        layout.addWidget(self.predecessor_combo)

        layout.addWidget(QLabel("<b>⏳ Estimare Durată PERT (ore):</b>"))
        self.time_o = QDoubleSpinBox();
        self.time_o.setRange(0.1, 500);
        self.time_o.setValue(8)
        self.time_p = QDoubleSpinBox();
        self.time_p.setRange(0.1, 500);
        self.time_p.setValue(12)
        self.time_m = QDoubleSpinBox();
        self.time_m.setRange(0.1, 500);
        self.time_m.setValue(20)

        layout.addWidget(QLabel("Optimist (O):"));
        layout.addWidget(self.time_o)
        layout.addWidget(QLabel("Probabil (P):"));
        layout.addWidget(self.time_p)
        layout.addWidget(QLabel("Pesimist (M):"));
        layout.addWidget(self.time_m)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def load_existing_tasks(self):
        url = f"http://localhost:8080/api/v1/tasks/project/{self.project_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                for t in res.json():
                    self.predecessor_combo.addItem(f"#{t['id']} - {t['titlu']}", userData=t['id'])
        except:
            pass

    def load_members(self):
        url = f"http://localhost:8080/api/v1/teams/{self.team_id}/members"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                member_ids = [m['userId'] for m in res.json()]
                details_res = requests.post("http://localhost:8080/api/v1/auth/users/details",
                                            headers=headers, json=member_ids)
                if details_res.status_code == 200:
                    for user in details_res.json():
                        name = f"{user.get('prenume', '')} {user.get('nume', '')}"
                        self.member_combo.addItem(name, userData=user['id'])
        except:
            pass

    def get_data(self):
        return {
            "projectId": self.project_id,
            "teamId": self.team_id,
            "atribuitLuiId": self.member_combo.currentData(),
            "titlu": self.title_input.text(),
            "predecesorId": self.predecessor_combo.currentData(),
            "timpOptimist": self.time_o.value(),
            "timpProbabil": self.time_p.value(),
            "timpPesimist": self.time_m.value(),
            "dataInceputEstimata": self.start_date_input.dateTime().toString("yyyy-MM-ddTHH:mm:ss"),
            "prioritate": "MEDIE"
        }