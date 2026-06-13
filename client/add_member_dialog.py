import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox,
                             QDialogButtonBox, QMessageBox)


class AddMemberDialog(QDialog):
    def __init__(self, token, current_user_id, parent=None):
        super().__init__(parent)
        self.token = token
        self.current_user_id = current_user_id
        self.setWindowTitle("👤 Adăugare Membru în Echipă")
        self.setFixedWidth(350)

        layout = QVBoxLayout(self)

        self.user_combo = QComboBox()
        layout.addWidget(QLabel("Selectează persoana din conexiunile tale:"))
        layout.addWidget(self.user_combo)

        self.load_connections()

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def load_connections(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            res = requests.get("http://localhost:8080/api/v1/auth/connections", headers=headers)
            if res.status_code == 200:
                conns = [c for c in res.json() if c['status'] == 'acceptat']

                partner_ids = []
                for c in conns:
                    if c['utilizator1Id'] == self.current_user_id:
                        partner_ids.append(c['utilizator2Id'])
                    else:
                        partner_ids.append(c['utilizator1Id'])

                if partner_ids:
                    details = requests.post("http://localhost:8080/api/v1/auth/users/details",
                                            headers=headers, json=partner_ids)
                    if details.status_code == 200:
                        for u in details.json():
                            name = f"{u.get('prenume', '')} {u.get('nume', '')}".strip()
                            self.user_combo.addItem(name or u['email'], userData=u['id'])
        except Exception as e:
            print(f"Eroare AddMemberDialog: {e}")

    def get_selected_user_id(self):
        return self.user_combo.currentData()