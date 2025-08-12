from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDateTimeEdit, QDialogButtonBox
from PyQt5.QtCore import QDateTime

class NewEventDialog(QDialog):
    def __init__(self,selected_date,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adauga Eveniment Nou")

        self.layout=QVBoxLayout(self)

        #Titlu
        self.title_input=QLineEdit()
        self.layout.addWidget(QLabel("Titlu:"))
        self.layout.addWidget(self.title_input)

        #Data si ora inceput
        self.start_datetime_input = QDateTimeEdit(selected_date.startOfDay())
        self.start_datetime_input.setCalendarPopup(True)
        self.layout.addWidget(QLabel("Data Început:"))
        self.layout.addWidget(self.start_datetime_input)

        # Selector pentru Data și ora de sfarsit
        self.end_datetime_input = QDateTimeEdit(selected_date.startOfDay().addSecs(3600))  # Default 1 oră
        self.end_datetime_input.setCalendarPopup(True)
        self.layout.addWidget(QLabel("Data Sfârșit:"))
        self.layout.addWidget(self.end_datetime_input)

        # Butoane OK și Cancel
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        return{
            "titlu": self.title_input.text(),
            "dataInceput": self.start_datetime_input.dateTime().toString("yyyy-MM-dd'T'HH:mm:ss"),
            "dataSfarsit": self.end_datetime_input.dateTime().toString("yyyy-MM-dd'T'HH:mm:ss")
        }