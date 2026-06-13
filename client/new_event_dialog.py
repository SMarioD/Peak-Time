from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDateTimeEdit, QDialogButtonBox
from PyQt5.QtCore import QDateTime

class NewEventDialog(QDialog):
    def __init__(self, start_date, end_date=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adaugă Eveniment Nou")
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        if end_date is None:
            end_date = start_date

        layout.addWidget(QLabel("Titlu:"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Data început:"))
        self.start_datetime_input = QDateTimeEdit(start_date.startOfDay().addSecs(8 * 3600))
        self.start_datetime_input.setCalendarPopup(True)
        layout.addWidget(self.start_datetime_input)

        layout.addWidget(QLabel("Data Sfârșit:"))
        self.end_datetime_input = QDateTimeEdit(end_date.startOfDay().addSecs(9 * 3600))
        self.end_datetime_input.setCalendarPopup(True)
        layout.addWidget(self.end_datetime_input)

        layout.addSpacing(4)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
    def get_data(self):
        return {
            "titlu": self.title_input.text(),
            "dataInceput": self.start_datetime_input.dateTime().toString("yyyy-MM-dd'T'HH:mm:ss"),
            "dataSfarsit": self.end_datetime_input.dateTime().toString("yyyy-MM-dd'T'HH:mm:ss")
        }