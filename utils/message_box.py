"""
Styled Message Box Utility
Provides consistent styled message boxes throughout the application
"""

from PyQt6.QtWidgets import QMessageBox


# Common stylesheet for message boxes
MESSAGE_BOX_STYLE = """
    QMessageBox {
        background-color: #FFFFFF;
    }
    QMessageBox QLabel {
        color: #1E293B;
        background: transparent;
        selection-background-color: transparent;
        selection-color: #1E293B;
        font-size: 13px;
        padding: 4px 8px;
        line-height: 1.5;
    }
    QMessageBox QPushButton {
        background-color: #3B82F6;
        color: white;
        padding: 8px 28px;
        border: none;
        border-radius: 6px;
        min-width: 90px;
        min-height: 32px;
        font-weight: 600;
        font-size: 13px;
    }
    QMessageBox QPushButton:hover {
        background-color: #2563EB;
    }
    QMessageBox QPushButton:pressed {
        background-color: #1D4ED8;
    }
"""


def show_info(parent, title, message):
    """Show an information message box"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setStyleSheet(MESSAGE_BOX_STYLE)
    msg.exec()


def show_warning(parent, title, message):
    """Show a warning message box"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setStyleSheet(MESSAGE_BOX_STYLE)
    msg.exec()


def show_error(parent, title, message):
    """Show an error/critical message box"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setStyleSheet(MESSAGE_BOX_STYLE)
    msg.exec()


def show_question(parent, title, message):
    """Show a question message box and return True if Yes was clicked"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(QMessageBox.Icon.Question)
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setStyleSheet(MESSAGE_BOX_STYLE)
    return msg.exec() == QMessageBox.StandardButton.Yes


def show_message(parent, title, message, msg_type="info"):
    """Dispatch to the appropriate message box based on msg_type"""
    if msg_type == "warning":
        show_warning(parent, title, message)
    elif msg_type == "error":
        show_error(parent, title, message)
    else:
        show_info(parent, title, message)
