import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QDialog
import requests
from main_window import MainWindow
from register_dialog import RegisterDialog


STYLESHEET = """
/* ----- Fereastra Principala & Dialoguri ----- */
QWidget, QDialog {
    background-color: #2b2b2b;
    color: #dcdcdc;
    font-family: "Segoe UI", Arial, sans-serif;
}

/* ----- Etichete (Labels) ----- */
QLabel {
    font-size: 14px;
    color: #a9b7c6;
}
QLabel#titleLabel {
    font-size: 26px;
    font-weight: bold;
    color: #ffffff;
    padding-bottom: 10px;
}

/* ----- Campuri de Text ----- */
QLineEdit {
    background-color: #3c3e41;
    border: 1px solid #555555;
    padding: 10px;
    border-radius: 5px;
    font-size: 14px;
    color: #dcdcdc;
}
QLineEdit:focus {
    border: 1px solid #007ACC;
}

/* ----- Dropdown (ComboBox) ----- */
QComboBox {
    background-color: #3c3e41;
    border: 1px solid #555555;
    padding: 8px;
    border-radius: 5px;
    font-size: 14px;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #3c3e41;
    selection-background-color: #007ACC;
    border: 1px solid #555555;
}

/* ----- Butoane ----- */
QPushButton {
    background-color: #007ACC;
    color: white;
    border: none;
    padding: 12px;
    border-radius: 5px;
    font-size: 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #008ae6;
}
QPushButton:pressed {
    background-color: #005A9E;
}
/* ----- Stil specific pentru butonul de inregistrare ----- */
QPushButton#registerButton {
    background-color: transparent;
    border: none;
    color: #0099FF;
    font-size: 12px;
    font-weight: normal;
    text-align: center;
    padding-top: 10px;
}
QPushButton#registerButton:hover {
    color: #FFFFFF;
    text-decoration: underline;
}

/* ----- Butoanele OK/Cancel din dialoguri ----- */
QDialogButtonBox QPushButton {
    min-width: 80px;
}

QCalendarWidget QWidget {
    alternate-background-color: #3c3e41;
}
QCalendarWidget QToolButton {
    color: #dcdcdc;
    background-color: transparent;
    border: none;
    padding: 5px;
    font-size: 14px;
    font-weight: bold;
}
QCalendarWidget QToolButton:hover {
    background-color: #555555;
    border-radius: 4px;
}
QCalendarWidget QAbstractItemView {
    selection-background-color: #007ACC;
    selection-color: #ffffff;
}
QCalendarWidget QAbstractItemView:enabled QTableView::item:first-child,
QCalendarWidget QAbstractItemView:enabled QTableView::item:last-child {
    color: #cc7832;
}

QCalendarWidget QAbstractItemView:enabled {
    color: #dcdcdc;
    selection-background-color: #007ACC;
    selection-color: #ffffff;
}
QCalendarWidget QAbstractItemView:disabled {
    color: #2b2b2b;
}
"""

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("loginWindow")
        self.setWindowTitle("Autentificare - Peak Time")
        self.setGeometry(100,100,350,320)
        self.initUI()
        self.main_win=None

    def initUI(self):
        layout=QVBoxLayout()

        #Camp pentru Email
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        #Camp pentru parola
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Parolă")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        layout.addSpacing(10)

        #Buton de login
        self.login_button=QPushButton("Autentificare",self)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # Buton de inregistrare
        self.register_button = QPushButton("Nu ai cont? Creează unul acum", self)
        self.register_button.setObjectName("registerButton")
        self.register_button.clicked.connect(self.handle_register_dialog)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def handle_register_dialog(self):
        dialog=RegisterDialog(self)
        if dialog.exec_()==QDialog.Accepted:
            data=dialog.get_data()
            if data:
                register_url="http://localhost:8080/api/v1/auth/register"
                try:
                    response=requests.post(register_url, json=data)
                    if response.status_code==201:
                        QMessageBox.information(self,"Succes","Contul a fost creat cu succes! Vă puteți autentifica acum.")
                    else:
                        error_data=response.json()
                        QMessageBox.critical(self,"Eroare la Înregistrare",error_data.get("error","A apărut o eroare."))
                except requests.exceptions.RequestException as e:
                    QMessageBox.critical(self,"Eoare de conexiune",str(e))


    def handle_login(self):
        email=self.email_input.text()
        parola=self.password_input.text()

        if not email or not parola:
            QMessageBox.warning(self,"Eroare","Va rugam introduceti email si parola.")
            return

        login_url="http://localhost:8080/api/v1/auth/login"

        payload={
            "email":email,
            "parola":parola
        }

        try:
            response = requests.post(login_url, json=payload)

            if response.status_code==200:
                response_data=response.json()
                jwt_token=response_data.get("token")
                user_id = response_data.get("userId")
                user_role = response_data.get("rol")

                print(f"Login reusit! Token: {jwt_token}")

                QMessageBox.information(self,"Succes","Autentificare reusita!")

                self.main_win=MainWindow(jwt_token,user_id,user_role)
                self.main_win.show()
                self.close()
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", "A apărut o eroare necunoscută.")
                except json.JSONDecodeError:
                    error_message = f"Răspuns server non-JSON: {response.text}"
                except Exception as ex:
                    error_message = f"Eroare la parsarea răspunsului de eroare: {ex}. Răspuns: {response.text}"

                QMessageBox.critical(self, "Eroare de Autentificare", error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", f"Nu s-a putut realiza conexiunea cu serverul: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())




