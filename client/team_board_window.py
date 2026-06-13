import requests
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QFrame, QPushButton,
                             QMessageBox, QLineEdit, QProgressBar, QDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from task_details_window import TaskDetailsWindow


class TaskCardItem(QListWidgetItem):
    def __init__(self, task):
        super().__init__()
        self.task_data = task


class TeamBoardWindow(QWidget):
    def __init__(self, team_id, team_name, project_id, token, current_user_id):
        super().__init__()
        self.team_id = team_id
        self.project_id = project_id
        self.token = token
        self.current_user_id = current_user_id
        self.names_map = {}

        self.setWindowTitle(f"Board Echipă: {team_name}")
        self.initUI()
        self.load_data()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_data_silent)
        self.refresh_timer.start(5000)

    def initUI(self):
        self.main_layout = QVBoxLayout(self)

        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame { background-color: #1A1927; border-radius: 10px; border: 1px solid #2D2B45; }
            QLabel { color: #A78BFA; font-weight: bold; font-size: 13px; }
        """)
        summary_layout = QHBoxLayout(self.summary_frame)

        self.lbl_team_progress = QLabel("📈 Progres Echipă: 0%")
        self.lbl_team_tasks = QLabel("📋 Sarcini: 0")
        self.lbl_team_delayed = QLabel("⚠️ Întârzieri: 0")

        summary_layout.addWidget(self.lbl_team_progress)
        summary_layout.addStretch()
        summary_layout.addWidget(self.lbl_team_tasks)
        summary_layout.addStretch()
        summary_layout.addWidget(self.lbl_team_delayed)

        self.main_layout.addWidget(self.summary_frame)

        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Caută după titlu sau angajat...")
        self.search_input.setStyleSheet("""
            QLineEdit { 
                padding: 10px; background: #1A1927; border: 1px solid #2D2B45; 
                border-radius: 20px; color: white;
            }
        """)
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input, 3)

        self.btn_only_mine = QPushButton("👤 Doar ale mele")
        self.btn_only_mine.setCheckable(True)
        self.btn_only_mine.setStyleSheet("""
            QPushButton { background: #2D2B45; color: #E2E8F0; padding: 10px 20px; border-radius: 20px; }
            QPushButton:checked { background: #7C3AED; color: white; font-weight: bold; }
        """)
        self.btn_only_mine.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.btn_only_mine)

        self.main_layout.addLayout(filter_layout)

        self.columns_layout = QHBoxLayout()
        self.lists = {
            "blocat": self.create_column("🚫 BLOCATE", "#EF4444"),
            "in asteptare": self.create_column("⏳ ÎN AȘTEPTARE", "#F59E0B"),
            "in progres": self.create_column("⚙️ ÎN LUCRU", "#7C3AED"),
            "finalizat": self.create_column("✅ FINALIZATE", "#10B981")
        }
        self.main_layout.addLayout(self.columns_layout)

    def create_column(self, title, color):
        col_wrap = QVBoxLayout()
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px; padding: 5px;")
        lbl.setAlignment(Qt.AlignCenter)
        col_wrap.addWidget(lbl)

        if "AȘTEPTARE" in title:
            btn_add = QPushButton("+ Adaugă Sarcină")
            btn_add.setStyleSheet("background-color: #2D2B45; color: white; border-radius: 5px; padding: 5px;")
            btn_add.clicked.connect(self.handle_add_task_to_team)
            col_wrap.addWidget(btn_add)

        list_w = QListWidget()
        list_w.itemDoubleClicked.connect(self.handle_task_double_click)
        list_w.setSpacing(8)
        list_w.setStyleSheet(f"border: 1px solid #2D2B45; border-radius: 8px; background: #0F0E17;")
        col_wrap.addWidget(list_w)

        self.columns_layout.addLayout(col_wrap)
        return list_w

    def load_data(self):
        url = f"http://localhost:8080/api/v1/tasks/team/{self.team_id}/board"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()

                user_ids = {t['atribuitLuiId'] for st in data.values() for t in st}
                if user_ids:
                    details = requests.post("http://localhost:8080/api/v1/auth/users/details",
                                            headers=headers, json=list(user_ids))
                    if details.status_code == 200:
                        self.names_map = {u['id']: f"{u.get('prenume', '')} {u.get('nume', '')}".strip() or u['email']
                                          for u in details.json()}

                total_tasks = 0
                completed = 0
                delayed = 0
                now = datetime.now()

                for status_key, tasks in data.items():
                    self.lists[status_key].clear()
                    for t in tasks:
                        total_tasks += 1
                        if t['status'] == 'finalizat': completed += 1

                        if t['status'] != 'finalizat' and t.get('dataSfarsitEstimata'):
                            try:
                                t_end = datetime.fromisoformat(t['dataSfarsitEstimata'].replace("Z", ""))
                                if t_end < now: delayed += 1
                            except:
                                pass

                        worker_name = self.names_map.get(t['atribuitLuiId'], f"ID: {t['atribuitLuiId']}")
                        item = TaskCardItem(t)
                        item.setText(f"📌 {t['titlu']}\n👤 {worker_name}\n⭐ {t['prioritate']}")
                        if t['prioritate'] == 'RIDICATA': item.setForeground(QColor("#EF4444"))
                        self.lists[status_key].addItem(item)

                prog_pct = int((completed / total_tasks * 100)) if total_tasks > 0 else 0
                self.lbl_team_progress.setText(f"📈 Progres Echipă: {prog_pct}%")
                self.lbl_team_tasks.setText(f"📋 Sarcini: {total_tasks}")
                self.lbl_team_delayed.setText(f"⚠️ Întârzieri: {delayed}")
                if delayed > 0: self.lbl_team_delayed.setStyleSheet("color: #EF4444; font-weight: bold;")

                self.apply_filters()

        except Exception as e:
            print(f"Eroare Board: {e}")

    def load_data_silent(self):
        if not self.search_input.hasFocus():
            self.load_data()

    def apply_filters(self):
        search_text = self.search_input.text().lower()
        show_only_mine = self.btn_only_mine.isChecked()

        for list_widget in self.lists.values():
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                task_data = getattr(item, 'task_data', {})
                match_search = search_text in item.text().lower()
                match_user = True
                if show_only_mine:
                    match_user = (task_data.get('atribuitLuiId') == self.current_user_id)
                item.setHidden(not (match_search and match_user))

    def handle_task_double_click(self, item):
        task_data = getattr(item, 'task_data', None)
        if task_data:
            dialog = TaskDetailsWindow(task_data, self.names_map, self.token, self)
            dialog.exec_()

    def handle_add_task_to_team(self):
        from assign_task_dialog import AssignTaskDialog
        dialog = AssignTaskDialog(self.team_id, self.project_id, self.token, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            res = requests.post("http://localhost:8080/api/v1/tasks",
                                headers={"Authorization": f"Bearer {self.token}"}, json=data)
            if res.status_code == 201:
                self.load_data()