import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QTimer

class ChatWindow(QWidget):
    def __init__(self,jwt_token,current_user_id,partner_user):
        super().__init__()
        self.jwt_token=jwt_token
        self.current_user_id=current_user_id
        self.partner_user=partner_user

        self.partner_id=self.partner_user.get('id')
        partner_email=self.partner_user.get('email','Necunoscut')

        self.setWindowTitle(f"Chat cu {partner_email}")
        self.setGeometry(250,250,400,500)
        self.initUI()

        self.load_conversation()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_conversation)
        self.timer.start(3000)

    def initUI(self):
        layout=QVBoxLayout()

        self.conversation_view=QTextEdit()
        self.conversation_view.setReadOnly(True)
        layout.addWidget(self.conversation_view)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Scrie un mesaj...")
        layout.addWidget(self.message_input)

        self.send_button=QPushButton("Trimite")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def load_conversation(self):
        conversation_url=f"http://localhost:8080/api/v1/messages/{self.partner_id}"
        headers={"Authorization":f"Bearer {self.jwt_token}"}

        try:
            response = requests.get(conversation_url, headers=headers)
            if response.status_code == 200:
                messages = response.json()
                scrollbar = self.conversation_view.verticalScrollBar()
                old_value = scrollbar.value()
                is_at_bottom = old_value == scrollbar.maximum()

                self.conversation_view.clear()
                for msg in messages:
                    prefix = "Eu: " if msg.get(
                        'senderId') == self.current_user_id else f"{self.partner_user.get('email')}: "
                    self.conversation_view.append(prefix + msg.get('continut'))
                if is_at_bottom:
                    scrollbar.setValue(scrollbar.maximum())
                else:
                    scrollbar.setValue(old_value)
        except requests.exceptions.RequestException as e:
            if not self.conversation_view.toPlainText():
                self.conversation_view.setText(f"Eroare de conexiune: {e}")

    def send_message(self):
        message_text = self.message_input.text().strip()
        if not message_text:
            return

        send_url = "http://localhost:8080/api/v1/messages"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        payload = {
            "receiverId": self.partner_id,
            "continut": message_text
        }

        try:
            response = requests.post(send_url, headers=headers, json=payload)
            if response.status_code == 202:
                self.message_input.clear()
            else:
                QMessageBox.critical(self, "Eroare la Trimitere", f"Serverul a răspuns cu o eroare: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()