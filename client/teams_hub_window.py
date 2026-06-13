import requests
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QFrame, QPushButton, QSplitter, QMessageBox, QComboBox,
                             QDialog)
from PyQt5.QtCore import Qt
from team_board_window import TeamBoardWindow
from link_project_dialog import LinkProjectDialog


class TeamsHubWindow(QWidget):
    def __init__(self, jwt_token, user_id):
        super().__init__()
        self.jwt_token = jwt_token
        self.user_id = user_id
        self.setWindowTitle("Management Echipe & Board-uri Kanban")
        self.resize(1300, 800)
        self.setStyleSheet("background-color: #0F0E17; color: #E2E8F0;")

        self.initUI()
        self.load_projects()
        self.load_teams()

    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.splitter = QSplitter(Qt.Horizontal)

        left_panel = QFrame()
        left_panel.setFixedWidth(280)
        left_panel.setStyleSheet("""
            QFrame { background-color: #1A1927; border-right: 1px solid #2D2B45; }
            QPushButton { text-align: left; padding-left: 10px; }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 15, 10, 15)

        left_layout.addWidget(QLabel("<b>🚀 PROIECT ACTIV</b>"))
        self.project_selector = QComboBox()
        self.project_selector.currentIndexChanged.connect(self.load_teams)
        left_layout.addWidget(self.project_selector)

        left_layout.addSpacing(20)

        left_layout.addWidget(QLabel("<b>👥 ECHIPELE TALE</b>"))
        self.teams_list = QListWidget()
        self.teams_list.itemClicked.connect(self.on_team_selected)
        left_layout.addWidget(self.teams_list)

        left_layout.addSpacing(10)

        actions_frame = QFrame()
        actions_frame.setStyleSheet("background: #161521; border-radius: 8px; border: 1px solid #2D2B45;")
        actions_layout = QVBoxLayout(actions_frame)

        self.btn_add_member = QPushButton("👤 Adaugă Membru")
        self.btn_add_member.setEnabled(False)
        self.btn_add_member.setStyleSheet("background: transparent; color: #E2E8F0; border: none; height: 30px;")
        self.btn_add_member.clicked.connect(self.handle_add_member)

        self.btn_link_project = QPushButton("🔗 Alocă Proiect")
        self.btn_link_project.setEnabled(False)
        self.btn_link_project.setStyleSheet("background: transparent; color: #E2E8F0; border: none; height: 30px;")
        self.btn_link_project.clicked.connect(self.handle_link_project)

        btn_add_team = QPushButton("➕ Echipă Nouă")
        btn_add_team.setStyleSheet(
            "background: transparent; color: #A78BFA; border: none; font-weight: bold; height: 30px;")
        btn_add_team.clicked.connect(self.handle_create_team)

        btn_add_project = QPushButton("🚀 Proiect Nou")
        btn_add_project.setStyleSheet(
            "background: transparent; color: #10B981; border: none; font-weight: bold; height: 30px;")
        btn_add_project.clicked.connect(self.handle_create_project)

        actions_layout.addWidget(self.btn_add_member)
        actions_layout.addWidget(self.btn_link_project)
        actions_layout.addWidget(btn_add_team)
        actions_layout.addWidget(btn_add_project)

        left_layout.addWidget(actions_frame)

        self.board_container = QWidget()
        self.board_layout = QVBoxLayout(self.board_container)
        self.board_layout.setContentsMargins(0, 0, 0, 0)

        self.placeholder_label = QLabel("Selectați o echipă pentru a vedea Board-ul.")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #64748B; font-size: 14px;")
        self.board_layout.addWidget(self.placeholder_label)

        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(self.board_container)
        main_layout.addWidget(self.splitter)

    def load_all(self):
        self.load_projects()
        self.load_teams()

    def load_projects(self):
        url = "http://localhost:8080/api/v1/teams/projects"
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                self.project_selector.blockSignals(True)
                self.project_selector.clear()
                self.project_selector.addItem("--- TOATE PROIECTELE ---", userData=None)
                for p in res.json():
                    self.project_selector.addItem(f"🚀 {p['nume']}", userData=p['id'])
                self.project_selector.blockSignals(False)
        except:
            pass

    def load_teams(self):
        project_id = self.project_selector.currentData()

        if project_id is None:
            url = "http://localhost:8080/api/v1/teams/my-teams"
        else:
            url = f"http://localhost:8080/api/v1/teams/project/{project_id}"

        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                self.teams_list.clear()
                teams = res.json()
                if not teams:
                    self.teams_list.addItem("Nicio echipă găsită.")
                    return

                for team in teams:
                    item = QListWidgetItem(f"👥 {team['nume']}")
                    item.setData(Qt.UserRole, team)
                    self.teams_list.addItem(item)
            else:
                print(f"Eroare server la încărcare echipe: {res.status_code}")
        except Exception as e:
            print(f"Eroare conexiune: {e}")

    def on_team_selected(self, item):
        team_data = item.data(Qt.UserRole)
        if not team_data or isinstance(team_data, str): return

        selected_project_id = self.project_selector.currentData()
        effective_project_id = selected_project_id if selected_project_id else team_data.get('projectId', 1)

        self.btn_add_member.setEnabled(True)
        self.btn_link_project.setEnabled(True)

        while self.board_layout.count():
            child = self.board_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        self.current_board = TeamBoardWindow(
            team_data['id'],
            team_data['nume'],
            effective_project_id,
            self.jwt_token,
            self.user_id
        )
        self.board_layout.addWidget(self.current_board)

    def handle_create_team(self):
        from create_team_dialog import CreateTeamDialog
        dialog = CreateTeamDialog(self.jwt_token, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            requests.post("http://localhost:8080/api/v1/teams",
                          headers={"Authorization": f"Bearer {self.jwt_token}"}, json=data)
            self.load_teams()

    def handle_create_project(self):
        from create_project_dialog import CreateProjectDialog
        dialog = CreateProjectDialog(self.jwt_token, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            requests.post("http://localhost:8080/api/v1/teams/projects",
                          headers={"Authorization": f"Bearer {self.jwt_token}"}, json=data)
            self.load_projects()

    def handle_add_member(self):
        if not self.teams_list.currentItem(): return
        team_data = self.teams_list.currentItem().data(Qt.UserRole)
        from add_member_dialog import AddMemberDialog
        dialog = AddMemberDialog(self.jwt_token, self.user_id, self)
        if dialog.exec_() == QDialog.Accepted:
            user_id = dialog.get_selected_user_id()
            requests.post(f"http://localhost:8080/api/v1/teams/{team_data['id']}/members",
                          headers={"Authorization": f"Bearer {self.jwt_token}"},
                          json={"userId": user_id, "rol": "MEMBER"})
            QMessageBox.information(self, "Succes", "Membru adăugat!")

    def handle_link_project(self):
        if not self.teams_list.currentItem(): return
        team_data = self.teams_list.currentItem().data(Qt.UserRole)

        from link_project_dialog import LinkProjectDialog
        dialog = LinkProjectDialog(self.jwt_token, self)

        if dialog.exec_() == QDialog.Accepted:
            project_id = dialog.get_selected_project_id()
            url = f"http://localhost:8080/api/v1/teams/{team_data['id']}/projects/{project_id}"
            headers = {"Authorization": f"Bearer {self.jwt_token}"}

            res = requests.post(url, headers=headers)
            if res.status_code == 200:
                QMessageBox.information(self, "Succes", "Echipa a primit proiectul!")
                self.load_teams()