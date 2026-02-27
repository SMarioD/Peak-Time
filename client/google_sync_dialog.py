import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QDialogButtonBox, QMessageBox)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl, Qt, QTimer


class GoogleSyncDialog(QDialog):
    def __init__(self, jwt_token, current_user_id, parent=None):
        super().__init__(parent)
        self.jwt_token = jwt_token
        self.current_user_id = current_user_id

        self.setWindowTitle("Sincronizează cu Google Calendar")
        self.setGeometry(200, 200, 450, 250)
        self.initUI()

        self.check_connection_status()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.status_label = QLabel("Status Google Calendar: Se verifică...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.connect_button = QPushButton("1. Conectează / Schimbă Contul Google")
        self.connect_button.clicked.connect(self.handle_google_connect)
        layout.addWidget(self.connect_button)

        self.refresh_status_button = QPushButton("2. Verifică Conexiunea (apasă după ce finalizezi în browser)")
        self.refresh_status_button.clicked.connect(self.check_connection_status)
        layout.addWidget(self.refresh_status_button)

        self.import_button = QPushButton("3. Importă Evenimente Google în Peak Time")
        self.import_button.clicked.connect(self.handle_google_import)
        self.import_button.setEnabled(False)
        self.import_button.setStyleSheet("background-color: #28a745; color: white;")
        layout.addWidget(self.import_button)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def check_connection_status(self):
        """Verifică dacă utilizatorul are un token salvat în DB"""
        status_url = f"http://localhost:8080/api/v1/external-calendar/google/status?userId={self.current_user_id}"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(status_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("connected"):
                    self.status_label.setText("Status Google Calendar: CONECTAT ✅")
                    self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
                    self.import_button.setEnabled(True)
                else:
                    self.status_label.setText("Status Google Calendar: NECONECTAT ❌")
                    self.import_button.setEnabled(False)
        except Exception as e:
            print(f"Eroare verificare status: {e}")

    def handle_google_connect(self):
        google_auth_url = f"http://localhost:8080/api/v1/external-calendar/google/link?userId={self.current_user_id}"
        QDesktopServices.openUrl(QUrl(google_auth_url))
        QMessageBox.information(self, "Autentificare Google",
                                "Browser-ul s-a deschis. Finalizează pașii acolo, apoi apasă 'Verifică Conexiunea' aici.")

    def handle_google_import(self):
        import_url = f"http://localhost:8080/api/v1/external-calendar/google/import?userId={self.current_user_id}"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}

        try:
            self.import_button.setText("Se importă... te rugăm așteaptă")
            self.import_button.setEnabled(False)

            response = requests.post(import_url, headers=headers)
            if response.status_code == 200:
                QMessageBox.information(self, "Succes", "Evenimentele Google au fost importate!")
                self.accept()
            else:
                QMessageBox.critical(self, "Eroare", f"Importul a eșuat: {response.text}")
                self.import_button.setEnabled(True)
                self.import_button.setText("3. Importă Evenimente Google în Peak Time")
        except Exception as e:
            QMessageBox.critical(self, "Eroare", str(e))
            self.import_button.setEnabled(True)