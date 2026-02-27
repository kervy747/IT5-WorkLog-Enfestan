"""
Login View - Modern Light Design
PyQt6 login screen with clean modern styling
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QGraphicsDropShadowEffect,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QColor, QPainter, QLinearGradient, QBrush
import qtawesome as qta
from utils.message_box import show_message

# Color palette – blends with the blue logo
BG_START = "#93C5FD"
BG_END   = "#60A5FA"
CARD_BG  = "#FFFFFF"
CARD_BORDER = "#BFDBFE"       # subtle blue border
INPUT_BG = "#F8FAFC"
INPUT_BORDER = "#CBD5E1"
INPUT_FOCUS = "#3B82F6"
PRIMARY = "#2563EB"           # matches logo blue
PRIMARY_HOVER = "#1D4ED8"
PRIMARY_PRESSED = "#1E40AF"
TEXT_DARK = "#1E293B"
TEXT_MEDIUM = "#475569"
TEXT_MUTED = "#94A3B8"
ACCENT_LIGHT = "#DBEAFE"
SUCCESS = "#10B981"
LOGO_BLUE = "#2563EB"         # logo's blue tone


class PasswordLineEdit(QWidget):
    """Custom password input with reveal toggle button"""

    def __init__(self, placeholder="Enter your password"):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(placeholder)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(46)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 12px 44px 12px 16px;
                font-size: 13px;
                border: 2px solid {INPUT_BORDER};
                border-radius: 10px;
                background-color: {INPUT_BG};
                color: {TEXT_DARK};
            }}
            QLineEdit:focus {{
                border: 2px solid {INPUT_FOCUS};
                background-color: white;
            }}
        """)

        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedSize(35, 35)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        try:
            self.toggle_btn.setIcon(qta.icon("fa5s.eye", color=TEXT_MUTED))
        except Exception:
            self.toggle_btn.setText("👁")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_password_visibility)
        self.is_visible = False

        layout.addWidget(self.password_input)
        self.toggle_btn.setParent(self.password_input)
        self.toggle_btn.move(self.password_input.width() - 40, 5)
        self.setLayout(layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.toggle_btn.move(self.password_input.width() - 40, 5)

    def toggle_password_visibility(self):
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            try:
                self.toggle_btn.setIcon(qta.icon("fa5s.eye-slash", color=PRIMARY))
            except Exception:
                self.toggle_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            try:
                self.toggle_btn.setIcon(qta.icon("fa5s.eye", color=TEXT_MUTED))
            except Exception:
                self.toggle_btn.setText("👁")

    def text(self):
        return self.password_input.text()

    def clear(self):
        self.password_input.clear()

    def setFocus(self):
        self.password_input.setFocus()


class LoginView(QWidget):
    """Login screen view with light modern design"""

    login_successful = pyqtSignal(dict, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def paintEvent(self, event):
        """Paint soft gradient background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(BG_START))
        gradient.setColorAt(1.0, QColor(BG_END))
        painter.fillRect(self.rect(), QBrush(gradient))
        painter.end()

    def init_ui(self):
        self.setWindowTitle("Work Log - Employee Attendance System")
        self.setFixedSize(440, 620)
        self.setStyleSheet("QWidget { background: transparent; }")

        # Outer layout to center the card
        outer = QVBoxLayout()
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(44, 36, 44, 36)

        # Card container
        card = QWidget()
        card.setObjectName("loginCard")
        card.setStyleSheet(f"""
            QWidget#loginCard {{
                background-color: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: 18px;
            }}
        """)

        # Blue-tinted drop shadow to match logo
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(37, 99, 235, 50))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(6)
        card_layout.setContentsMargins(38, 36, 38, 28)

        # Logo
        logo_label = QLabel()
        logo_label.setFixedSize(96, 96)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("background: transparent; border: none;")
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        card_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        card_layout.addSpacing(8)

        # Title
        title = QLabel("Work Log")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {TEXT_DARK};")
        card_layout.addWidget(title)

        subtitle = QLabel("EMPLOYEE ATTENDANCE SYSTEM")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 10px; font-weight: 800; color: {TEXT_MUTED}; letter-spacing: 3px; margin-bottom: 2px;")
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(18)

        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet(f"font-size: 12px; color: {TEXT_MEDIUM}; font-weight: 600;")
        card_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(46)
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 12px 16px;
                font-size: 13px;
                border: 2px solid {INPUT_BORDER};
                border-radius: 10px;
                background-color: {INPUT_BG};
                color: {TEXT_DARK};
            }}
            QLineEdit:focus {{
                border: 2px solid {INPUT_FOCUS};
                background-color: white;
            }}
        """)
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(4)

        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet(f"font-size: 12px; color: {TEXT_MEDIUM}; font-weight: 600;")
        card_layout.addWidget(password_label)

        self.password_widget = PasswordLineEdit("Enter your password")
        self.password_input = self.password_widget.password_input
        card_layout.addWidget(self.password_widget)

        card_layout.addSpacing(18)

        # Login button
        self.login_button = QPushButton("  Sign In")
        self.login_button.setMinimumHeight(48)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        try:
            self.login_button.setIcon(qta.icon("fa5s.sign-in-alt", color="white"))
        except Exception:
            pass
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                font-size: 14px;
                font-weight: 700;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {PRIMARY_PRESSED};
            }}
        """)

        # Button glow
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(18)
        btn_shadow.setColor(QColor(59, 130, 246, 80))
        btn_shadow.setOffset(0, 4)
        self.login_button.setGraphicsEffect(btn_shadow)

        self.login_button.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_button)

        self.password_input.returnPressed.connect(self.handle_login)

        card_layout.addSpacing(10)

        # Footer
        try:
            lock_icon = qta.icon("fa5s.lock", color=TEXT_MUTED)
            footer_icon = QLabel()
            footer_icon.setPixmap(lock_icon.pixmap(11, 11))
            footer_icon.setStyleSheet("background: transparent;")
            footer_text = QLabel("Secure Login")
            footer_text.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
            footer_row = QHBoxLayout()
            footer_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
            footer_row.setSpacing(5)
            footer_row.addWidget(footer_icon)
            footer_row.addWidget(footer_text)
            footer_widget = QWidget()
            footer_widget.setLayout(footer_row)
            card_layout.addWidget(footer_widget)
        except Exception:
            footer = QLabel("Secure Login")
            footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
            footer.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
            card_layout.addWidget(footer)

        card.setLayout(card_layout)
        outer.addWidget(card)

        self.setLayout(outer)

    def handle_login(self):
        from controllers.login_controller import LoginController
        username = self.username_input.text().strip().replace(" ", "")
        password = self.password_widget.text()
        controller = LoginController()
        user, title, message, msg_type = controller.authenticate(username, password)
        show_message(self, title, message, msg_type)
        if user:
            self.login_successful.emit(user, user['role'])
            self.close()

    def clear_inputs(self):
        self.username_input.clear()
        self.password_widget.clear()
