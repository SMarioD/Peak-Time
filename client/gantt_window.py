import math
import requests
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt, QRectF, QPointF, QThread, pyqtSignal
from PyQt5.QtGui import (
    QColor, QPen, QBrush, QFont, QPainter, QLinearGradient, QTransform
)
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsScene, QGraphicsView, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsLineItem,
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QMessageBox, QProgressBar, QFrame, QToolTip
)

BG          = QColor("#0F0E17")
BG_CARD     = QColor("#1A1927")
BG_ROW_ALT  = QColor("#15131F")
ACCENT      = QColor("#7C3AED")
ACCENT2     = QColor("#A78BFA")
TEXT_MAIN   = QColor("#E2E8F0")
TEXT_MUTED  = QColor("#64748B")
GRID        = QColor("#252336")
BORDER      = QColor("#2D2B45")

STATUS_COLORS = {
    "finalizat":    QColor("#10B981"),
    "in progres":   QColor("#7C3AED"),
    "in asteptare": QColor("#F59E0B"),
    "blocat":       QColor("#EF4444"),
}

PRIORITY_STRIPE = {
    "RIDICATA": QColor("#EF4444"),
    "MEDIE":    QColor("#F59E0B"),
    "SCAZUTA":  QColor("#10B981"),
}

ROW_H       = 65
ROW_PAD     = 12
LABEL_W     = 300
HEADER_H    = 80
DAY_W       = 85
MIN_BAR_W   = 15


class GanttLoader(QThread):
    loaded  = pyqtSignal(list)
    error   = pyqtSignal(str)

    def __init__(self, project_id: int, token: str, base_url: str):
        super().__init__()
        self.project_id = project_id
        self.token      = token
        self.base_url   = base_url

    def run(self):
        try:
            url = f"{self.base_url}/api/v1/tasks/project/{self.project_id}/gantt"
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            self.loaded.emit(resp.json())
        except Exception as e:
            self.error.emit(str(e))


class GanttScene(QGraphicsScene):

    def __init__(self, tasks: list):
        super().__init__()
        self.tasks = tasks
        self.setBackgroundBrush(QBrush(BG))
        self._build()

    def _build(self):
        self.clear()
        if not self.tasks:
            self._draw_empty()
            return

        dates = []
        for t in self.tasks:
            for field in ("dataInceputEstimata", "dataSfarsitEstimata", "dataFinalizare"):
                v = t.get(field)
                if v:
                    try:
                        dates.append(datetime.fromisoformat(v[:19]))
                    except Exception:
                        pass

        if not dates:
            self._draw_empty()
            return

        self.start_date = min(dates).replace(hour=0, minute=0, second=0)
        self.end_date   = max(dates).replace(hour=23, minute=59, second=59)

        self.start_date -= timedelta(days=1)
        self.end_date   += timedelta(days=1)

        total_days = (self.end_date - self.start_date).days + 1
        self.total_days = total_days

        scene_w = LABEL_W + total_days * DAY_W
        scene_h = HEADER_H + len(self.tasks) * ROW_H

        self.setSceneRect(0, 0, scene_w, scene_h)

        self._draw_header(total_days)
        self._draw_rows(total_days)
        self._draw_grid(total_days)
        self._draw_bars()
        self._draw_dependency_arrows()
        self._draw_today_line()

    def _draw_header(self, total_days: int):
        bg_rect = self.addRect(
            0, 0, LABEL_W + total_days * DAY_W + 40, HEADER_H,
            QPen(Qt.NoPen), QBrush(BG_CARD)
        )

        self._add_text("Sarcină", 10, 18, bold=True, color=TEXT_MAIN, size=10)
        self._add_text("Responsabil  |  Progres", 10, 34, bold=False, color=TEXT_MUTED, size=8)

        sep = self.addLine(LABEL_W, 0, LABEL_W, HEADER_H,
                           QPen(BORDER, 1))

        cur = self.start_date
        for i in range(total_days):
            x = LABEL_W + i * DAY_W
            is_weekend = cur.weekday() >= 5
            is_today   = cur.date() == datetime.today().date()

            if is_weekend:
                self.addRect(x, 0, DAY_W, HEADER_H,
                             QPen(Qt.NoPen), QBrush(QColor(30, 27, 50)))

            if is_today:
                self.addRect(x, 0, DAY_W, HEADER_H + len(self.tasks) * ROW_H + 40,
                             QPen(Qt.NoPen), QBrush(QColor(124, 58, 237, 18)))

            color = ACCENT2 if is_today else (TEXT_MUTED if is_weekend else TEXT_MAIN)
            self._add_text(str(cur.day), x + DAY_W // 2 - 6, 8,
                           bold=is_today, color=color, size=9)

            if cur.day == 1 or i == 0:
                self._add_text(cur.strftime("%B %Y"), x + 5, 50, bold=True, color=ACCENT, size=10)

            cur += timedelta(days=1)

    def _draw_rows(self, total_days: int):
        w = LABEL_W + total_days * DAY_W + 40
        for i, task in enumerate(self.tasks):
            y = HEADER_H + i * ROW_H
            color = BG_CARD if i % 2 == 0 else BG_ROW_ALT

            self.addRect(0, y, w, ROW_H, QPen(Qt.NoPen), QBrush(color))

            prio = task.get("prioritate", "MEDIE")
            stripe_color = PRIORITY_STRIPE.get(prio, PRIORITY_STRIPE["MEDIE"])
            self.addRect(0, y + 2, 3, ROW_H - 4,
                         QPen(Qt.NoPen), QBrush(stripe_color))

            titlu = task.get("titlu", "—")
            if len(titlu) > 24:
                titlu = titlu[:22] + "…"
            self._add_text(titlu, 8, y + 8, bold=False, color=TEXT_MAIN, size=9)

            progres = task.get("progres", 0)
            self._draw_mini_progress(8, y + 26, 140, progres)

            self.addLine(0, y + ROW_H - 1, w, y + ROW_H - 1,
                         QPen(GRID, 1))

    def _draw_grid(self, total_days: int):
        scene_h = HEADER_H + len(self.tasks) * ROW_H + 40
        for i in range(total_days + 1):
            x = LABEL_W + i * DAY_W
            pen = QPen(GRID, 1, Qt.SolidLine)
            if (self.start_date + timedelta(days=i)).day == 1:
                pen = QPen(BORDER, 1)
            self.addLine(x, HEADER_H, x, scene_h, pen)

        self.addLine(LABEL_W, 0, LABEL_W,
                     HEADER_H + len(self.tasks) * ROW_H + 40,
                     QPen(BORDER, 1))

    def _draw_bars(self):
        for i, task in enumerate(self.tasks):
            y     = HEADER_H + i * ROW_H + ROW_PAD
            bar_h = ROW_H - ROW_PAD * 2

            start_str = task.get("dataInceputEstimata")
            end_str   = task.get("dataSfarsitEstimata")
            if not start_str or not end_str:
                continue

            try:
                t_start = datetime.fromisoformat(start_str[:19])
                t_end   = datetime.fromisoformat(end_str[:19])
            except Exception:
                continue

            x_start = self._date_to_x(t_start)
            x_end   = self._date_to_x(t_end)
            bar_w   = max(MIN_BAR_W, x_end - x_start)

            status = task.get("status", "in asteptare")
            color  = STATUS_COLORS.get(status, STATUS_COLORS["in asteptare"])

            bar_bg = self.addRect(
                x_start, y, bar_w, bar_h,
                QPen(color.darker(130), 1),
                QBrush(color.darker(170))
            )
            bar_bg.setZValue(1)

            progres = task.get("progres", 0) / 100.0
            prog_w  = bar_w * progres
            if prog_w > 0:
                bar_prog = self.addRect(
                    x_start, y, prog_w, bar_h,
                    QPen(Qt.NoPen),
                    QBrush(color)
                )
                bar_prog.setZValue(2)

            if bar_w > 40:
                pct_text = f"{task.get('progres', 0)}%"
                txt = self._add_text(pct_text,
                                     x_start + bar_w / 2 - 12,
                                     y + bar_h / 2 - 6,
                                     bold=True, color=QColor("#FFFFFF"), size=8)
                txt.setZValue(3)

            fin_str = task.get("dataFinalizare")
            if fin_str:
                try:
                    fin = datetime.fromisoformat(fin_str[:19])
                    if fin > t_end and status == "finalizat":
                        x_late = self._date_to_x(fin)
                        late_line = self.addLine(
                            x_late, y, x_late, y + bar_h,
                            QPen(QColor("#EF4444"), 2)
                        )
                        late_line.setZValue(4)
                except Exception:
                    pass

    def _draw_dependency_arrows(self):
        id_to_row = {t.get("id"): i for i, t in enumerate(self.tasks)}

        for i, task in enumerate(self.tasks):
            pred_id = task.get("predecesorId")
            if pred_id is None:
                continue
            j = id_to_row.get(pred_id)
            if j is None:
                continue

            pred = self.tasks[j]
            end_str = pred.get("dataSfarsitEstimata")
            if not end_str:
                continue
            try:
                t_end = datetime.fromisoformat(end_str[:19])
            except Exception:
                continue

            x1 = self._date_to_x(t_end)
            y1 = HEADER_H + j * ROW_H + ROW_H // 2

            start_str = task.get("dataInceputEstimata")
            if not start_str:
                continue
            try:
                t_start = datetime.fromisoformat(start_str[:19])
            except Exception:
                continue

            x2 = self._date_to_x(t_start)
            y2 = HEADER_H + i * ROW_H + ROW_H // 2

            pen = QPen(ACCENT2, 1.5, Qt.DashLine)
            pen.setDashPattern([4, 3])

            mid_x = (x1 + x2) / 2
            self.addLine(x1, y1, mid_x, y1, pen).setZValue(0)
            self.addLine(mid_x, y1, mid_x, y2, pen).setZValue(0)
            self.addLine(mid_x, y2, x2, y2, pen).setZValue(0)

            arrow_pen = QPen(ACCENT2, 1.5)
            self.addLine(x2, y2, x2 - 6, y2 - 4, arrow_pen).setZValue(0)
            self.addLine(x2, y2, x2 - 6, y2 + 4, arrow_pen).setZValue(0)

    def _draw_today_line(self):
        today = datetime.today()
        if not (self.start_date <= today <= self.end_date):
            return
        x = self._date_to_x(today)
        scene_h = HEADER_H + len(self.tasks) * ROW_H + 40
        pen = QPen(ACCENT, 2, Qt.SolidLine)
        line = self.addLine(x, HEADER_H, x, scene_h, pen)
        line.setZValue(5)

        self._add_text("azi", x - 12, HEADER_H - 16,
                        bold=True, color=ACCENT2, size=8).setZValue(5)

    def _date_to_x(self, dt: datetime) -> float:
        delta = (dt - self.start_date).total_seconds()
        day_seconds = 86400.0
        return LABEL_W + (delta / day_seconds) * DAY_W

    def _add_text(self, text: str, x: float, y: float,
                  bold: bool = False, color: QColor = TEXT_MAIN,
                  size: int = 9) -> QGraphicsTextItem:
        item = QGraphicsTextItem(text)
        font = QFont("Segoe UI", size)
        font.setBold(bold)
        item.setFont(font)
        item.setDefaultTextColor(color)
        item.setPos(x, y)
        self.addItem(item)
        return item

    def _draw_mini_progress(self, x: float, y: float, w: float, pct: int):
        h = 5
        # Track
        self.addRect(x, y, w, h, QPen(Qt.NoPen), QBrush(GRID))
        # Fill
        fill_w = w * pct / 100
        if fill_w > 0:
            color = QColor("#10B981") if pct == 100 else ACCENT
            self.addRect(x, y, fill_w, h, QPen(Qt.NoPen), QBrush(color))

    def _draw_empty(self):
        self.setSceneRect(0, 0, 600, 300)
        self._add_text("Nu există sarcini cu date planificate pentru acest proiect.",
                       60, 130, bold=False, color=TEXT_MUTED, size=11)


class GanttView(QGraphicsView):
    def __init__(self, scene=None):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QBrush(BG))
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._zoom = 1.0

    def auto_fit(self):
        if not self.scene(): return
        rect = self.scene().sceneRect()

        if rect.width() > 0:
            view_w = self.viewport().width()
            scale = view_w / rect.width()
            final_scale = min(scale, 1.5)
            self.setTransform(QTransform().scale(final_scale, final_scale))
            self.horizontalScrollBar().setValue(0)
            self.verticalScrollBar().setValue(0)

    def wheelEvent(self, event):
        factor = 1.12 if event.angleDelta().y() > 0 else 1 / 1.12
        self._zoom *= factor
        self._zoom = max(0.3, min(3.0, self._zoom))
        from PyQt5.QtGui import QTransform
        self.setTransform(QTransform().scale(self._zoom, self._zoom))


class GanttWindow(QMainWindow):

    def __init__(self, project_id, token, base_url="http://localhost:8080", project_name="Proiect", parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.token = token
        self.base_url = base_url
        self.setWindowTitle(f"Gantt - {project_name}")
        self.showMaximized()

        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self.btn_refresh = QPushButton(f"↻ REÎNCARCĂ DATE PROIECT: {project_name.upper()}")
        self.btn_refresh.setFixedHeight(50)
        self.btn_refresh.setStyleSheet(f"""
            background: {ACCENT.name()}; 
            color: white; 
            font-weight: bold; 
            font-size: 14px; 
            border: none;
        """)
        self.btn_refresh.clicked.connect(self._load_data)
        self.main_layout.addWidget(self.btn_refresh)
        self.view = GanttView()
        self.main_layout.addWidget(self.view)

        self._load_data()



    def _build_legend(self) -> QWidget:
        legend = QWidget()
        legend.setFixedHeight(36)
        legend.setStyleSheet(f"background:{BG_CARD.name()};")
        h = QHBoxLayout(legend)
        h.setContentsMargins(16, 6, 16, 6)
        h.setSpacing(20)

        for label, color in [
            ("Finalizat",    "#10B981"),
            ("În progres",   "#7C3AED"),
            ("În așteptare", "#F59E0B"),
            ("Blocat",       "#EF4444"),
        ]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; font-size:14px;")
            txt = QLabel(label)
            txt.setStyleSheet(f"color:{TEXT_MUTED.name()}; font-size:10px;")
            h.addWidget(dot)
            h.addWidget(txt)

        h.addStretch()

        today_line = QLabel("—")
        today_line.setStyleSheet(f"color:{ACCENT.name()}; font-size:12px; font-weight:bold;")
        today_txt = QLabel("Azi")
        today_txt.setStyleSheet(f"color:{TEXT_MUTED.name()}; font-size:10px;")
        h.addWidget(today_line)
        h.addWidget(today_txt)

        dep_line = QLabel("- - -")
        dep_line.setStyleSheet(f"color:{ACCENT2.name()}; font-size:10px;")
        dep_txt = QLabel("Dependență")
        dep_txt.setStyleSheet(f"color:{TEXT_MUTED.name()}; font-size:10px;")
        h.addWidget(dep_line)
        h.addWidget(dep_txt)

        return legend

    def _load_data(self):
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setText("⏳ SE ÎNCARCĂ...")
        self.loader = GanttLoader(self.project_id, self.token, self.base_url)
        self.loader.loaded.connect(self._show_gantt)
        self.loader.error.connect(self._on_load_error)
        self.loader.start()

    def _show_gantt(self, tasks):
        new_scene = GanttScene(tasks)
        self.view.setScene(new_scene)
        self.btn_refresh.setEnabled(True)
        self.btn_refresh.setText(f"↻ REÎNCARCĂ DATE PROIECT")
        if tasks:
            self.view.auto_fit()


    def _on_load_error(self, msg):
        self.btn_refresh.setEnabled(True)
        self.btn_refresh.setText("↻ REÎNCARCĂ (EROARE)")
        QMessageBox.critical(self, "Eroare la încărcare", msg)
    def _apply_style(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: {BG.name()};
                color: {TEXT_MAIN.name()};
                font-family: 'Segoe UI', sans-serif;
            }}
            QScrollBar:horizontal {{
                background: {BG_CARD.name()};
                height: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: {ACCENT.name()};
                border-radius: 5px;
                min-width: 30px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
        """)

    def _btn_style(self) -> str:
        return f"""
            QPushButton {{
                background: {ACCENT.name()};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                background: {ACCENT.darker(110).name()};
            }}
            QPushButton:disabled {{
                background: {BORDER.name()};
                color: {TEXT_MUTED.name()};
            }}
        """