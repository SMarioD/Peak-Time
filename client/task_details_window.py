import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QFrame, QProgressBar, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSize


class TaskDetailsWindow(QDialog):
    def __init__(self, task, names_map, token, parent=None):
        super().__init__(parent)
        self.task = task
        self.names_map = names_map
        self.token = token
        self.setWindowTitle(f"Detalii Task: {task['titlu']}")
        self.resize(550, 650)  # Am mărit puțin fereastra
        self.setStyleSheet("background-color: #1A1927; color: #E2E8F0;")
        self.initUI()
        self.load_history()

    def initUI(self):
        layout = QVBoxLayout(self)
        info_card = QFrame()
        info_card.setStyleSheet("background-color: #2D2B45; border-radius: 10px; padding: 15px;")
        info_layout = QVBoxLayout(info_card)

        worker_name = self.names_map.get(self.task['atribuitLuiId'], f"ID: {self.task['atribuitLuiId']}")
        info_layout.addWidget(QLabel(f"<h2 style='color: #7C3AED;'>📌 {self.task['titlu']}</h2>"))
        info_layout.addWidget(QLabel(f"<b>👤 Responsabil:</b> {worker_name}"))
        info_layout.addWidget(
            QLabel(f"<b>📊 Status Curent:</b> <span style='color: #10B981;'>{self.task['status'].upper()}</span>"))
        info_layout.addWidget(QLabel(f"<b>⭐ Prioritate:</b> {self.task['prioritate']}"))

        desc = self.task.get('descriere') or "Nicio descriere furnizată."
        info_layout.addWidget(QLabel(f"\n<b>📝 Descriere:</b>\n{desc}"))
        layout.addWidget(info_card)

        layout.addSpacing(10)
        layout.addWidget(QLabel("<b>📈 Progres Realizat:</b>"))
        self.prog_bar = QProgressBar()
        self.prog_bar.setFixedHeight(25)
        self.prog_bar.setValue(self.task.get('progres', 0))
        self.prog_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #444; border-radius: 12px; text-align: center; background: #0F0E17; }
            QProgressBar::chunk { background-color: #7C3AED; border-radius: 10px; }
        """)
        layout.addWidget(self.prog_bar)

        layout.addSpacing(10)
        layout.addWidget(QLabel("<b>📜 Istoric Activitate (Audit Log):</b>"))

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("background-color: #0F0E17; border: 1px solid #2D2B45; padding: 5px;")

        self.history_list.setWordWrap(True)

        self.history_list.itemDoubleClicked.connect(self.on_history_item_clicked)
        self.history_list.setSpacing(8)

        layout.addWidget(self.history_list)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def on_history_item_clicked(self, item):
        from PyQt5.QtWidgets import QMessageBox

        full_text = item.text()

        msg = QMessageBox(self)
        msg.setWindowTitle("Detalii Intrare Istoric")
        msg.setText(full_text)
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("background-color: #1A1927; color: white;")
        msg.exec_()

    def load_history(self):
        url = f"http://localhost:8080/api/v1/statistics/task/{self.task['id']}/history"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                self.history_list.clear()
                for entry in res.json():
                    dt = entry['timestamp'].replace("T", " ")[:16]
                    user = self.names_map.get(entry['modificatDeId'], f"User {entry['modificatDeId']}")
                    text = f"🕒 {dt} | Modificat de: {user}\n↳ Status setat la: {entry['statusNou'].upper()}"

                    item = QListWidgetItem(text)
                    item.setSizeHint(QSize(0, 50))

                    self.history_list.addItem(item)
            else:
                self.history_list.addItem("Nu există istoric disponibil.")
        except Exception as e:
            self.history_list.addItem(f"Eroare la încărcare istoric: {e}")