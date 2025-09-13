import json
import threading
import asyncio
import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import websockets

class ChatWindow(QWidget):
    message_received = pyqtSignal(str)

    def __init__(self, jwt_token, current_user_id, partner_user):
        super().__init__()
        self.jwt_token = jwt_token
        self.current_user_id = current_user_id
        self.partner_user = partner_user

        self.partner_id = self.partner_user.get('id')
        partner_email = self.partner_user.get('email', 'Necunoscut')

        self.setWindowTitle(f"Chat cu {partner_email}")
        self.setGeometry(250, 250, 400, 500)
        self.initUI()
        self.load_conversation()

        self.message_received.connect(self.append_message_to_view)

        self.ws_thread = threading.Thread(target=self.run_websocket_client)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def initUI(self):
        layout = QVBoxLayout()
        self.conversation_view = QTextEdit()
        self.conversation_view.setReadOnly(True)
        layout.addWidget(self.conversation_view)
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Scrie un mesaj...")
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)
        self.send_button = QPushButton("Trimite")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)
        self.setLayout(layout)

    def load_conversation(self):
        conversation_url = f"http://localhost:8080/api/v1/messages/{self.partner_id}"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            response = requests.get(conversation_url, headers=headers)
            if response.status_code == 200:
                messages = response.json()
                self.conversation_view.clear()
                for msg in messages:
                    prefix = "Eu: " if msg.get('senderId') == self.current_user_id else f"{self.partner_user.get('email')}: "
                    self.conversation_view.append(prefix + msg.get('continut'))
        except requests.exceptions.RequestException as e:
            self.conversation_view.setText(f"Eroare de conexiune: {e}")

    def append_message_to_view(self, message_json):
        try:
            msg = json.loads(message_json)
            if (msg.get('senderId') == self.current_user_id and msg.get('receiverId') == self.partner_id) or \
               (msg.get('senderId') == self.partner_id and msg.get('receiverId') == self.current_user_id):
                prefix = "Eu: " if msg.get('senderId') == self.current_user_id else f"{self.partner_user.get('email')}: "
                self.conversation_view.append(prefix + msg.get('continut'))
        except json.JSONDecodeError:
            print(f"Mesaj WebSocket invalid primit: {message_json}")

    def run_websocket_client(self):
        asyncio.run(self.websocket_listener())

    async def websocket_listener(self):
        uri = "ws://localhost:8080/ws"
        try:
            async with websockets.connect(uri) as websocket:
                connect_frame = f"CONNECT\naccept-version:1.2\nheart-beat:10000,10000\nAuthorization:Bearer {self.jwt_token}\n\n\x00"
                await websocket.send(connect_frame)
                print("Frame CONNECT trimis.")

                connected_response = await websocket.recv()
                if "CONNECTED" in str(connected_response):
                    print("Conexiune STOMP stabilită cu succes!")
                else:
                    print(f"Eroare la conectare STOMP: {connected_response}")
                    return

                destination = f"/topic/messages/{self.current_user_id}"
                subscribe_frame = f"SUBSCRIBE\nid:sub-{self.current_user_id}\ndestination:{destination}\n\n\x00"
                await websocket.send(subscribe_frame)
                print(f"Subscris la {destination}")

                async for message in websocket:
                    if message.startswith("MESSAGE"):
                        parts = message.split('\n\n', 1)
                        if len(parts) > 1:
                            body = parts[1].rstrip('\x00')
                            self.message_received.emit(body)
        except Exception as e:
            print(f"Eroare WebSocket: {e}")

    def send_message(self):
        message_text = self.message_input.text().strip()
        if not message_text:
            return

        send_url = "http://localhost:8080/api/v1/messages"
        headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
        payload = {"receiverId": self.partner_id, "continut": message_text}
        try:
            response = requests.post(send_url, headers=headers, json=payload)
            if response.status_code == 202:
                self.message_input.clear()
            else:
                QMessageBox.critical(self, "Eroare la Trimitere", f"Serverul a răspuns cu o eroare: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Eroare de Conexiune", str(e))

    def closeEvent(self, event):
        event.accept()