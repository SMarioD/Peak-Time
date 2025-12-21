from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Creează Cont Nou")
        self.setGeometry(150, 150, 350, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.nume_input = QLineEdit()
        layout.addWidget(QLabel("Nume:"))
        layout.addWidget(self.nume_input)

        self.prenume_input = QLineEdit()
        layout.addWidget(QLabel("Prenume:"))
        layout.addWidget(self.prenume_input)

        self.email_input = QLineEdit()
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        self.parola_input = QLineEdit()
        self.parola_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Parolă:"))
        layout.addWidget(self.parola_input)

        self.rol_combo = QComboBox()
        self.rol_combo.addItems(["utilizator", "angajat", "team_leader"])
        layout.addWidget(QLabel("Tip Cont:"))
        layout.addWidget(self.rol_combo)

        layout.addSpacing(20)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self):
        if not all(
                [self.nume_input.text(), self.prenume_input.text(), self.email_input.text(), self.parola_input.text()]):
            QMessageBox.warning(self, "Câmpuri Incomplete", "Toate câmpurile sunt obligatorii.")
            return None

        return {
            "nume": self.nume_input.text(),
            "prenume": self.prenume_input.text(),
            "email": self.email_input.text(),
            "parola": self.parola_input.text(),
            "rol": self.rol_combo.currentText()
        }