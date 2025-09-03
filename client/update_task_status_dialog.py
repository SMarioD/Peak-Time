from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QDialogButtonBox


class UpdateTaskStatusDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Actualizează Status Sarcină")
        self.selected_status = None

        self.layout = QVBoxLayout(self)

        self.in_proces_button = QPushButton("În Proces")
        self.in_proces_button.clicked.connect(lambda: self.set_status("in proces"))

        self.problematic_button = QPushButton("Problematic")
        self.problematic_button.clicked.connect(lambda: self.set_status("problematic"))

        self.finalizat_button = QPushButton("Finalizat")
        self.finalizat_button.clicked.connect(lambda: self.set_status("finalizat"))

        self.layout.addWidget(self.in_proces_button)
        self.layout.addWidget(self.problematic_button)
        self.layout.addWidget(self.finalizat_button)

        self.cancel_button = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.cancel_button.rejected.connect(self.reject)
        self.layout.addWidget(self.cancel_button)

    def set_status(self, status):
        self.selected_status = status
        self.accept()

    def get_selected_status(self):
        return self.selected_status