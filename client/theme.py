from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

C = {
    # Fundal
    "bg_deep":    "#0d0d12",
    "bg_base":    "#13131a",
    "bg_surface": "#1a1a24",
    "bg_raised":  "#22223a",
    "bg_overlay": "#2a2a42",

    "accent":     "#7c6af7",
    "accent_dim": "#5b52c4",
    "accent_glow":"#9d8fff",
    "accent_muted":"#3d3670",

    "indigo":     "#6366f1",
    "indigo_dim": "#4f46e5",

    # Text
    "text_primary":  "#e8e6f4",
    "text_secondary":"#9e9cbd",
    "text_muted":    "#5e5c78",
    "text_inverse":  "#ffffff",

    # Status
    "success": "#34d399",
    "warning": "#fbbf24",
    "danger":  "#f87171",
    "info":    "#60a5fa",

    # Border
    "border":       "#2e2c4a",
    "border_focus": "#7c6af7",
    "border_subtle":"#1e1c30",
}

STYLESHEET = f"""

/*BAZA — Ferestre, Dialoguri, Widget-ur*/

QWidget, QDialog, QMainWindow {{
    background-color: {C['bg_base']};
    color: {C['text_primary']};
    font-family: "Segoe UI", "SF Pro Display", sans-serif;
    font-size: 13px;
}}

QDialog {{
    background-color: {C['bg_surface']};
    border: 1px solid {C['border']};
    border-radius: 12px;
}}

/*ETICHETE*/

QLabel {{
    color: {C['text_secondary']};
    font-size: 13px;
    background: transparent;
}}

QLabel#titleLabel {{
    font-size: 22px;
    font-weight: 700;
    color: {C['text_primary']};
    letter-spacing: -0.5px;
}}

QLabel#sectionLabel {{
    font-size: 11px;
    font-weight: 600;
    color: {C['text_muted']};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/*CAMPURI DE TEXT*/

QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {C['bg_raised']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 9px 12px;
    font-size: 13px;
    color: {C['text_primary']};
    selection-background-color: {C['accent_muted']};
    selection-color: {C['text_primary']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {C['border_focus']};
    background-color: {C['bg_overlay']};
    outline: none;
}}

QLineEdit:hover, QTextEdit:hover {{
    border: 1px solid {C['accent_muted']};
}}

QLineEdit::placeholder {{
    color: {C['text_muted']};
}}

/*BUTOANE*/

QPushButton {{
    background-color: {C['accent']};
    color: {C['text_inverse']};
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.2px;
}}

QPushButton:hover {{
    background-color: {C['accent_glow']};
}}

QPushButton:pressed {{
    background-color: {C['accent_dim']};
}}

QPushButton:disabled {{
    background-color: {C['bg_raised']};
    color: {C['text_muted']};
}}

/* Buton secundar */
QPushButton#secondaryButton {{
    background-color: transparent;
    border: 1px solid {C['border']};
    color: {C['text_secondary']};
}}

QPushButton#secondaryButton:hover {{
    border-color: {C['accent']};
    color: {C['accent_glow']};
    background-color: {C['accent_muted']};
}}

/* Buton pericol */
QPushButton#dangerButton {{
    background-color: transparent;
    border: 1px solid {C['danger']};
    color: {C['danger']};
}}

QPushButton#dangerButton:hover {{
    background-color: rgba(248, 113, 113, 0.12);
}}

/* Buton succes */
QPushButton#successButton {{
    background-color: {C['success']};
    color: #0d1f17;
}}

QPushButton#successButton:hover {{
    background-color: #6ee7b7;
}}

/* Buton ghost */
QPushButton#ghostButton, QPushButton#registerButton {{
    background-color: transparent;
    border: none;
    color: {C['accent_glow']};
    font-size: 12px;
    font-weight: 500;
    padding: 6px;
    text-decoration: none;
}}

QPushButton#ghostButton:hover, QPushButton#registerButton:hover {{
    color: {C['text_primary']};
    text-decoration: underline;
}}

/* Buton meniu hamburger */
QPushButton#menuButton {{
    background-color: {C['bg_raised']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    color: {C['text_secondary']};
    font-size: 16px;
    font-weight: bold;
    padding: 4px 8px;
}}

QPushButton#menuButton:hover {{
    background-color: {C['accent_muted']};
    border-color: {C['accent']};
    color: {C['accent_glow']};
}}

/*LISTE*/

QListWidget {{
    background-color: {C['bg_surface']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    color: {C['text_primary']};
    outline: none;
    padding: 4px;
}}

QListWidget::item {{
    padding: 9px 12px;
    border-radius: 6px;
    margin: 1px 2px;
    color: {C['text_primary']};
    border: none;
}}

QListWidget::item:hover {{
    background-color: {C['bg_raised']};
    color: {C['text_primary']};
}}

QListWidget::item:selected {{
    background-color: {C['accent_muted']};
    color: {C['accent_glow']};
    border: none;
}}

/*TABELE*/

QTableWidget {{
    background-color: {C['bg_surface']};
    alternate-background-color: {C['bg_raised']};
    gridline-color: {C['border_subtle']};
    color: {C['text_primary']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    outline: none;
}}

QTableWidget::item {{
    padding: 8px 12px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {C['accent_muted']};
    color: {C['accent_glow']};
}}

QHeaderView::section {{
    background-color: {C['bg_overlay']};
    color: {C['text_muted']};
    padding: 10px 12px;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    border: none;
    border-bottom: 1px solid {C['border']};
}}

QHeaderView::section:first {{
    border-top-left-radius: 10px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 10px;
}}

/*SCROLLBAR*/

QScrollBar:vertical {{
    background: {C['bg_surface']};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {C['accent_muted']};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {C['accent']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}

QScrollBar:horizontal {{
    background: {C['bg_surface']};
    height: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {C['accent_muted']};
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {C['accent']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
    background: none;
}}

/*CALENDAR*/

QCalendarWidget {{
    background-color: {C['bg_surface']};
    border: 1px solid {C['border']};
    border-radius: 12px;
}}

QCalendarWidget QWidget {{
    background-color: {C['bg_surface']};
    alternate-background-color: {C['bg_raised']};
}}

QCalendarWidget QToolButton {{
    color: {C['text_primary']};
    background-color: transparent;
    border: none;
    padding: 6px 10px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 6px;
}}

QCalendarWidget QToolButton:hover {{
    background-color: {C['bg_raised']};
    color: {C['accent_glow']};
}}

QCalendarWidget QToolButton#qt_calendar_prevmonth,
QCalendarWidget QToolButton#qt_calendar_nextmonth {{
    color: {C['accent']};
    font-size: 16px;
    font-weight: bold;
}}

QCalendarWidget QSpinBox {{
    background-color: {C['bg_raised']};
    color: {C['text_primary']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 3px 6px;
}}

QCalendarWidget QAbstractItemView {{
    background-color: {C['bg_surface']};
    color: {C['text_primary']};
    selection-background-color: {C['accent']};
    selection-color: {C['text_inverse']};
    outline: none;
}}

QCalendarWidget QAbstractItemView:enabled {{
    color: {C['text_primary']};
    selection-background-color: {C['accent']};
    selection-color: {C['text_inverse']};
}}

QCalendarWidget QAbstractItemView:disabled {{
    color: {C['text_muted']};
}}

/* Weekend-uri — portocaliu subtil */
QCalendarWidget QAbstractItemView:enabled QTableView::item:first-child,
QCalendarWidget QAbstractItemView:enabled QTableView::item:last-child {{
    color: {C['warning']};
}}

/*DROPDOWN / COMBOBOX*/

QComboBox {{
    background-color: {C['bg_raised']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: {C['text_primary']};
    min-width: 120px;
}}

QComboBox:hover {{
    border-color: {C['accent_muted']};
}}

QComboBox:focus {{
    border-color: {C['border_focus']};
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {C['text_muted']};
    width: 0;
    height: 0;
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {C['bg_overlay']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    color: {C['text_primary']};
    selection-background-color: {C['accent_muted']};
    selection-color: {C['accent_glow']};
    padding: 4px;
    outline: none;
}}

/*SPINBOX*/

QSpinBox, QDoubleSpinBox, QDateTimeEdit {{
    background-color: {C['bg_raised']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 13px;
    color: {C['text_primary']};
}}

QSpinBox:focus, QDoubleSpinBox:focus, QDateTimeEdit:focus {{
    border-color: {C['border_focus']};
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QDateTimeEdit::up-button, QDateTimeEdit::down-button {{
    background-color: {C['bg_overlay']};
    border: none;
    border-radius: 4px;
    width: 18px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {C['accent_muted']};
}}

QDateTimeEdit::drop-down {{
    border: none;
    width: 22px;
    background: {C['bg_overlay']};
    border-radius: 4px;
}}

/*MENIU CONTEXTUAL*/

QMenu {{
    background-color: {C['bg_overlay']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    padding: 6px;
    color: {C['text_primary']};
}}

QMenu::item {{
    padding: 9px 20px 9px 14px;
    border-radius: 6px;
    font-size: 13px;
    color: {C['text_primary']};
}}

QMenu::item:selected {{
    background-color: {C['accent_muted']};
    color: {C['accent_glow']};
}}

QMenu::item:disabled {{
    color: {C['text_muted']};
}}

QMenu::separator {{
    height: 1px;
    background: {C['border']};
    margin: 4px 8px;
}}

/*DIALOG BUTTONS*/

QDialogButtonBox QPushButton {{
    min-width: 80px;
    padding: 8px 16px;
}}

/*MESSAGEBOX*/

QMessageBox {{
    background-color: {C['bg_surface']};
    color: {C['text_primary']};
}}

QMessageBox QLabel {{
    color: {C['text_primary']};
    font-size: 13px;
    min-width: 300px;
    qproperty-alignment: AlignCenter;
}}

QMessageBox QPushButton {{
    min-width: 80px;
}}

/*TOOLTIP*/

QToolTip {{
    background-color: {C['bg_overlay']};
    color: {C['text_primary']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/*GROUPBOX*/

QGroupBox {{
    background-color: {C['bg_surface']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    margin-top: 16px;
    padding: 12px;
    font-weight: 600;
    color: {C['text_secondary']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {C['accent_glow']};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}

/*SPLITTER*/

QSplitter::handle {{
    background-color: {C['border']};
    width: 1px;
    height: 1px;
}}

/*CHECKBOX / RADIOBUTTON*/

QCheckBox, QRadioButton {{
    color: {C['text_secondary']};
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {C['border']};
    border-radius: 4px;
    background: {C['bg_raised']};
}}

QCheckBox::indicator:checked {{
    background: {C['accent']};
    border-color: {C['accent']};
}}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border-color: {C['accent']};
}}

QRadioButton::indicator {{
    border-radius: 8px;
}}

QRadioButton::indicator:checked {{
    background: {C['accent']};
    border-color: {C['accent']};
}}

"""


def apply_palette(app):
    palette = QPalette()

    bg           = QColor(C['bg_base'])
    bg_surface   = QColor(C['bg_surface'])
    bg_raised    = QColor(C['bg_raised'])
    text_primary = QColor(C['text_primary'])
    text_sec     = QColor(C['text_secondary'])
    text_muted   = QColor(C['text_muted'])
    accent       = QColor(C['accent'])
    border       = QColor(C['border'])

    palette.setColor(QPalette.Window,          bg)
    palette.setColor(QPalette.WindowText,      text_primary)
    palette.setColor(QPalette.Base,            bg_surface)
    palette.setColor(QPalette.AlternateBase,   bg_raised)
    palette.setColor(QPalette.Text,            text_primary)
    palette.setColor(QPalette.BrightText,      QColor("#ffffff"))
    palette.setColor(QPalette.ButtonText,      text_primary)
    palette.setColor(QPalette.Button,          bg_raised)
    palette.setColor(QPalette.Highlight,       accent)
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipBase,     QColor(C['bg_overlay']))
    palette.setColor(QPalette.ToolTipText,     text_primary)
    palette.setColor(QPalette.Link,            QColor(C['accent_glow']))
    palette.setColor(QPalette.LinkVisited,     QColor(C['indigo']))

    palette.setColor(QPalette.Disabled, QPalette.WindowText, text_muted)
    palette.setColor(QPalette.Disabled, QPalette.Text,       text_muted)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, text_muted)
    palette.setColor(QPalette.Disabled, QPalette.Button,     bg_surface)

    app.setPalette(palette)

class SuccessDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Succes")
        self.setFixedWidth(300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(12)

        icon_label = QLabel("✓")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 32px; color: {C['success']}; background: transparent;")
        layout.addWidget(icon_label)

        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {C['text_primary']}; font-size: 13px; background: transparent;")
        layout.addWidget(msg_label)

        ok_button = QPushButton("OK")
        ok_button.setFixedHeight(36)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

class InfoDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignLeft)
        msg_label.setStyleSheet(f"color: {C['text_primary']}; font-size: 13px; background: transparent;")
        layout.addWidget(msg_label)

        ok_button = QPushButton("OK")
        ok_button.setFixedHeight(36)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)