import sys
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QLineEdit,QPushButton,QVBoxLayout,QMessageBox
import requests
from main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autentificare - Peak Time")
        self.setGeometry(100,100,300,200)
        self.initUI()
        self.main_win=None

    def initUI(self):
        layout=QVBoxLayout()

        #Camp pentru Email
        self.email_label=QLabel("Email:")
        self.email_input=QLineEdit(self)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        #Camp pentru parola
        self.password_label = QLabel("Parola:")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        #Buton de login
        self.login_button=QPushButton("Login",self)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # TODO: Adaugam un buton de inregistrare

        self.setLayout(layout)

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

                print(f"Login reusit! Token: {jwt_token}")

                QMessageBox.information(self,"Succes","Autentificare reusita!")

                self.main_win=MainWindow(jwt_token)
                self.main_win.show()
                self.close()
            else:
                error_data=response.json()
                error_message=error_data.get("error","A aparut o eroare necunoscuta.")
                QMessageBox.critical(self,"Eroare de Autentificare",error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", f"Nu s-a putut realiza conexiunea cu serverul: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())




