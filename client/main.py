import os
import sys
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.wayland.debug=false"
os.environ["XDG_SESSION_TYPE"] = "x11"
import json
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QDialog, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from theme import SuccessDialog
from main_window import MainWindow
from register_dialog import RegisterDialog
from theme import STYLESHEET, apply_palette
from gantt_window import GanttWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("loginWindow")
        self.setWindowTitle("Peak Time")
        self.setFixedSize(400, 480)
        self.initUI()
        self.main_win = None

    def initUI(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)
        card.setObjectName("loginCard")
        card.setStyleSheet("""
            QFrame#loginCard {
                background-color: #1a1a24;
                border: 1px solid #2e2c4a;
                border-radius: 16px;
            }
        """)
        outer.addWidget(card, alignment=Qt.AlignCenter)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 24, 40, 24)
        layout.setSpacing(10)

        logo_row = QHBoxLayout()
        dot = QLabel("⬡")
        dot.setStyleSheet("font-size: 24px; color: #7c6af7; background: transparent;")
        title = QLabel("Peak Time")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            color: #e8e6f4;
            background: transparent;
            letter-spacing: -0.5px;
        """)
        logo_row.addWidget(dot)
        logo_row.addWidget(title)
        logo_row.addStretch()
        layout.addLayout(logo_row)

        subtitle = QLabel("Autentifică-te în cont")
        subtitle.setStyleSheet("color: #5e5c78; font-size: 13px; background: transparent; margin-bottom: 8px;")
        layout.addWidget(subtitle)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #2e2c4a; background: #2e2c4a; border: none; max-height: 1px;")
        layout.addWidget(sep)
        layout.addSpacing(4)

        email_label = QLabel("Email")
        email_label.setStyleSheet("color: #9e9cbd; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("nume@exemplu.com")
        self.email_input.setFixedHeight(42)
        layout.addWidget(self.email_input)
        pass_label = QLabel("Parolă")
        pass_label.setStyleSheet("color: #9e9cbd; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(pass_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(42)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)


        self.login_button = QPushButton("Autentificare")
        self.login_button.setFixedHeight(44)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #2e2c4a; background: #2e2c4a; border: none; max-height: 1px; margin-top: 4px;")
        layout.addWidget(sep2)

        self.register_button = QPushButton("Nu ai cont? Creează unul acum")
        self.register_button.setObjectName("registerButton")
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.clicked.connect(self.handle_register_dialog)
        layout.addWidget(self.register_button, alignment=Qt.AlignCenter)
        card.setFixedSize(360, 400)

    def handle_register_dialog(self):
        dialog = RegisterDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                try:
                    response = requests.post("http://localhost:8080/api/v1/auth/register", json=data)
                    if response.status_code == 201:
                        SuccessDialog("Contul a fost creat! Te poți autentifica acum.", self).exec_()
                    else:
                        error_data = response.json()
                        QMessageBox.critical(self, "Eroare la înregistrare", error_data.get("error", "A apărut o eroare."))
                except requests.exceptions.RequestException as e:
                    QMessageBox.critical(self, "Eroare de conexiune", str(e))

    def handle_login(self):
        email = self.email_input.text().strip()
        parola = self.password_input.text()

        if not email or not parola:
            QMessageBox.warning(self, "Câmpuri incomplete", "Te rugăm introduceți email și parolă.")
            return

        try:
            response = requests.post(
                "http://localhost:8080/api/v1/auth/login",
                json={"email": email, "parola": parola}
            )
            if response.status_code == 200:
                data = response.json()
                jwt_token = data.get("token")
                user_id   = data.get("userId")
                user_role = data.get("rol")

                self.main_win = MainWindow(jwt_token, user_id, user_role)
                self.main_win.show()
                self.close()
            else:
                try:
                    error_msg = response.json().get("error", "Eroare necunoscută.")
                except json.JSONDecodeError:
                    error_msg = f"Răspuns non-JSON: {response.text}"
                QMessageBox.critical(self, "Autentificare eșuată", error_msg)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de conexiune", str(e))

    


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    app.setStyleSheet(STYLESHEET)
    apply_palette(app)

    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())