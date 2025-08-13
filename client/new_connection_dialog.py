from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox


class NewConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adaugă Conexiune Nouă")

        self.layout = QVBoxLayout(self)

        # Camp pentru Email
        self.email_input = QLineEdit()
        self.layout.addWidget(QLabel("Introduceți email-ul utilizatorului:"))
        self.layout.addWidget(self.email_input)

        # Butoane OK si Cancel
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_email(self):
        return self.email_input.text()