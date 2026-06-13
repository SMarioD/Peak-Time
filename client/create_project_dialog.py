import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QTextEdit, QDialogButtonBox, QMessageBox)

class CreateProjectDialog(QDialog):
    def __init__(self, token, parent=None):
        super().__init__(parent)
        self.token = token
        self.setWindowTitle("🚀 Proiect Nou")
        self.setFixedWidth(350)
        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Numele Proiectului")
        layout.addWidget(QLabel("Nume Proiect:"))
        layout.addWidget(self.name_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("O scurtă descriere...")
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(QLabel("Descriere:"))
        layout.addWidget(self.desc_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self):
        return {
            "nume": self.name_input.text(),
            "descriere": self.desc_input.toPlainText()
        }