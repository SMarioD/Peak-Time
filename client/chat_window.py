import json
import asyncio
import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
import websockets

class WebSocketWorker(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, jwt_token, user_id):
        super().__init__()
        self.jwt_token = jwt_token
        self.current_user_id = user_id
        self.running = True
        self.loop = None
        self.websocket = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.websocket_listener())
        except Exception as e:
            print(f"Loop oprit: {e}")
        finally:
            self.loop.close()

    def stop(self):
        self.running = False
        if self.websocket and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)

    async def websocket_listener(self):
        uri = "ws://localhost:8080/ws"
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                connect_frame = f"CONNECT\naccept-version:1.2\nheart-beat:10000,10000\nAuthorization:Bearer {self.jwt_token}\n\n\x00"
                await websocket.send(connect_frame)
                destination = f"/topic/messages/{self.current_user_id}"
                subscribe_frame = f"SUBSCRIBE\nid:sub-{self.current_user_id}\ndestination:{destination}\n\n\x00"
                await websocket.send(subscribe_frame)
                async for message in websocket:
                    if not self.running:
                        break
                    if message.startswith("MESSAGE"):
                        parts = message.split('\n\n', 1)
                        if len(parts) > 1:
                            body = parts[1].rstrip('\x00')
                            self.message_received.emit(body)
        except Exception as e:
            print(f"Eroare WebSocket Worker: {e}")
        finally:
            self.websocket = None


class ChatWindow(QWidget):
    message_received_signal = pyqtSignal(str)

    def __init__(self, jwt_token, current_user_id, partner_user):
        super().__init__()
        self.jwt_token = jwt_token
        self.current_user_id = current_user_id
        self.partner_user = partner_user
        self.partner_id = self.partner_user.get('id')

        self.setWindowTitle(f"Chat cu {self.partner_user.get('email')}")
        self.setGeometry(250, 250, 400, 500)
        self.initUI()
        self.load_conversation()

        self.thread = QThread()
        self.worker = WebSocketWorker(jwt_token, current_user_id)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.message_received.connect(self.append_message_to_view)
        self.thread.start()

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

    def append_message_to_view(self, message_json):
        try:
            msg = json.loads(message_json)
            if (msg.get('senderId') == self.partner_id) or (msg.get('senderId') == self.current_user_id):
                prefix = "Eu: " if msg.get(
                    'senderId') == self.current_user_id else f"{self.partner_user.get('email')}: "
                self.conversation_view.append(prefix + msg.get('continut'))
        except:
            pass

    def send_message(self):
        text = self.message_input.text().strip()
        if not text: return
        try:
            res = requests.post("http://localhost:8080/api/v1/messages",
                                headers={"Authorization": f"Bearer {self.jwt_token}"},
                                json={"receiverId": self.partner_id, "continut": text})
            if res.status_code == 202: self.message_input.clear()
        except:
            pass

    def load_conversation(self):
        try:
            res = requests.get(f"http://localhost:8080/api/v1/messages/{self.partner_id}",
                               headers={"Authorization": f"Bearer {self.jwt_token}"})
            if res.status_code == 200:
                for msg in res.json():
                    prefix = "Eu: " if msg.get(
                        'senderId') == self.current_user_id else f"{self.partner_user.get('email')}: "
                    self.conversation_view.append(prefix + msg.get('continut'))
        except:
            pass

    def closeEvent(self, event):
        self.worker.stop()
        self.thread.quit()
        self.thread.finished.connect(self.thread.deleteLater)
        event.accept()