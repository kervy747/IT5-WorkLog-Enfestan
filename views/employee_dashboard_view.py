"""
Employee Dashboard View - Modern Sidebar Design
PyQt6 employee dashboard with sidebar navigation
Employee role: View own attendance, late records, analytics, requests, and reports
"""

import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QMessageBox, QDateEdit, QComboBox, QFormLayout, QStackedWidget,
    QScrollArea, QFrame, QGridLayout, QSizePolicy, QSpacerItem, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate, QSize
from PyQt6.QtGui import QPixmap, QColor, QBrush, QFont
import qtawesome as qta
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from controllers.attendance_controller import AttendanceController
from controllers.staff_dashboard_controller import StaffDashboardController
from controllers.reports_controller import ReportsController
from views.user_account_view import ChangePasswordDialog
from utils.message_box import show_info, show_warning, show_error, show_message, show_question


# ===== COLOR PALETTE (Light Theme) =====
SIDEBAR_BG = "#FFFFFF"
SIDEBAR_HOVER = "#F1F5F9"
SIDEBAR_ACTIVE = "#3B82F6"
SIDEBAR_TEXT = "#64748B"
SIDEBAR_TEXT_ACTIVE = "#3B82F6"
SIDEBAR_BORDER = "#E2E8F0"
CONTENT_BG = "#F1F5F9"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E2E8F0"
HEADER_BG = "#FFFFFF"
PRIMARY = "#3B82F6"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER = "#EF4444"
INFO = "#06B6D4"
TEXT_PRIMARY = "#1E293B"
TEXT_SECONDARY = "#64748B"
TEXT_MUTED = "#94A3B8"

# Light background mapping for icon containers
LIGHT_BG = {
    "#3B82F6": "#DBEAFE",
    "#10B981": "#D1FAE5",
    "#F59E0B": "#FEF3C7",
    "#EF4444": "#FEE2E2",
    "#06B6D4": "#CFFAFE",
    "#64748B": "#F1F5F9",
    "#1E293B": "#E2E8F0",
    "#94A3B8": "#F1F5F9",
}

def get_light_bg(color):
    return LIGHT_BG.get(color, "#F1F5F9")


class CenteredTableWidget(QTableWidget):
    """QTableWidget that auto-centers all item text"""
    def setItem(self, row, column, item):
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        super().setItem(row, column, item)


class SidebarButton(QPushButton):
    """Modern sidebar navigation button with icon"""

    def __init__(self, icon_name, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self.setIconSize(QSize(20, 20))

        try:
            icon = qta.icon(icon_name, color=SIDEBAR_TEXT)
            self.setIcon(icon)
        except Exception:
            pass

        self._icon_name = icon_name
        self._update_style(False)

    def _update_style(self, active):
        text_color = SIDEBAR_TEXT_ACTIVE if active else SIDEBAR_TEXT
        bg_color = "#EFF6FF" if active else "transparent"
        hover_bg = SIDEBAR_HOVER
        border_left = f"3px solid {SIDEBAR_ACTIVE}" if active else "3px solid transparent"

        try:
            icon = qta.icon(self._icon_name, color=text_color)
            self.setIcon(icon)
        except Exception:
            pass

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-left: {border_left};
                border-radius: 0px;
                text-align: left;
                padding: 12px 20px 12px 16px;
                font-size: 13px;
                font-weight: {'600' if active else '500'};
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                color: {SIDEBAR_ACTIVE};
            }}
        """)

    def setChecked(self, checked):
        super().setChecked(checked)
        self._update_style(checked)


class StatCard(QWidget):
    """Modern stat card with icon, value, and label"""

    def __init__(self, icon_name, title, value="0", color=PRIMARY, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.color = color

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        icon_container = QLabel()
        icon_container.setFixedSize(48, 48)
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            icon = qta.icon(icon_name, color=color)
            icon_container.setPixmap(icon.pixmap(QSize(24, 24)))
        except Exception:
            icon_container.setText("")
        icon_container.setStyleSheet(f"""
            background-color: {get_light_bg(color)};
            border-radius: 12px;
            border: none;
        """)
        layout.addWidget(icon_container)
        self._icon_container = icon_container
        self._icon_name = icon_name

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; border: none;")
        text_layout.addWidget(self.value_label)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY}; border: none;")
        text_layout.addWidget(self.title_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        self.setLayout(layout)
        self.setStyleSheet(f"""
            QWidget#statCard {{
                background-color: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
            }}
        """)

    def set_value(self, value, color=None):
        self.value_label.setText(str(value))
        if color:
            self.color = color
            try:
                icon = qta.icon(self._icon_name, color=color)
                self._icon_container.setPixmap(icon.pixmap(QSize(24, 24)))
            except Exception:
                pass
            self._icon_container.setStyleSheet(f"""
                background-color: {get_light_bg(color)};
                border-radius: 12px;
                border: none;
            """)


class EmployeeDashboardView(QWidget):
    """Employee dashboard view with modern sidebar"""

    finished = pyqtSignal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.employee_id = user_data['employee_id']

        # Initialize controllers
        self.attendance_controller = AttendanceController(self.employee_id)
        self.dashboard_controller = StaffDashboardController(self.employee_id)
        self.reports_controller = ReportsController()

        self.init_ui()
        self.load_data()

        # Defer notifications until after the window is shown
        QTimer.singleShot(300, self._check_notifications)

        # Setup timer for real-time clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

    def init_ui(self):
        """Initialize the modern sidebar UI"""
        self.setWindowTitle("Work Log - Employee Dashboard")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(f"background-color: {CONTENT_BG};")

        # Root horizontal layout
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ===== SIDEBAR =====
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background-color: {SIDEBAR_BG};")
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo / Brand Section
        brand = QWidget()
        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(20, 20, 20, 20)
        brand_layout.setSpacing(12)

        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("WL")
            logo_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: white; background-color: {SIDEBAR_ACTIVE}; border-radius: 8px; padding: 6px;")
            logo_label.setFixedSize(36, 36)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_layout.addWidget(logo_label)

        brand_text = QLabel("Work Log")
        brand_text.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRIMARY};")
        brand_layout.addWidget(brand_text)
        brand_layout.addStretch()
        brand.setLayout(brand_layout)
        sidebar_layout.addWidget(brand)

        # Separator
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {SIDEBAR_BORDER};")
        sidebar_layout.addWidget(sep)

        # User Info
        user_section = QWidget()
        user_layout = QVBoxLayout()
        user_layout.setContentsMargins(20, 16, 20, 16)
        user_layout.setSpacing(4)

        user_name_label = QLabel(self.user_data['full_name'])
        user_name_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {TEXT_PRIMARY};")
        user_layout.addWidget(user_name_label)

        user_role_label = QLabel("Employee")
        user_role_label.setStyleSheet("""
            font-size: 11px; color: #059669;
            background-color: #D1FAE5;
            padding: 2px 10px; border-radius: 10px;
            font-weight: 600;
        """)
        user_role_label.setFixedWidth(75)
        user_layout.addWidget(user_role_label)

        # Shift info
        shift = self.dashboard_controller.get_employee_shift(self.user_data['employee_id'])
        if shift:
            shift_display = self.dashboard_controller.format_shift_display(shift)
            shift_label = QLabel(f"  {shift_display}")
            shift_label.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; margin-top: 4px;")
            shift_label.setWordWrap(True)
            user_layout.addWidget(shift_label)

        user_section.setLayout(user_layout)
        sidebar_layout.addWidget(user_section)

        # Separator
        sep2 = QWidget()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background-color: {SIDEBAR_BORDER};")
        sidebar_layout.addWidget(sep2)

        # Navigation Label
        nav_label = QLabel("  NAVIGATION")
        nav_label.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {SIDEBAR_TEXT}; padding: 16px 20px 8px 20px; letter-spacing: 1px;")
        sidebar_layout.addWidget(nav_label)

        # Navigation Buttons
        self.nav_buttons = []
        nav_items = [
            ("fa5s.clock", "Attendance Records"),
            ("fa5s.exclamation-triangle", "Late Records"),
            ("fa5s.chart-bar", "Analytics"),
            ("fa5s.clipboard-list", "My Requests"),
            ("fa5s.file-alt", "Reports"),
        ]

        for icon_name, text in nav_items:
            btn = SidebarButton(icon_name, f"  {text}")
            btn.clicked.connect(lambda checked, b=btn: self._on_nav_clicked(b))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Separator
        sep3 = QWidget()
        sep3.setFixedHeight(1)
        sep3.setStyleSheet(f"background-color: {SIDEBAR_BORDER};")
        sidebar_layout.addWidget(sep3)

        # Bottom actions
        change_pwd_btn = SidebarButton("fa5s.key", "  Change Password")
        change_pwd_btn.setCheckable(False)
        change_pwd_btn.clicked.connect(self.show_change_password_dialog)
        sidebar_layout.addWidget(change_pwd_btn)

        logout_btn = QPushButton("  Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFixedHeight(48)
        logout_btn.setIconSize(QSize(20, 20))
        try:
            logout_btn.setIcon(qta.icon("fa5s.sign-out-alt", color=DANGER))
        except Exception:
            pass
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {DANGER};
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
                padding: 12px 20px 12px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #FEE2E2;
            }}
        """)
        logout_btn.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(logout_btn)

        sidebar_layout.addSpacing(12)

        sidebar.setLayout(sidebar_layout)
        root_layout.addWidget(sidebar)

        # Sidebar divider
        sidebar_divider = QWidget()
        sidebar_divider.setFixedWidth(1)
        sidebar_divider.setStyleSheet(f"background-color: {SIDEBAR_BORDER};")
        root_layout.addWidget(sidebar_divider)

        # ===== MAIN CONTENT AREA =====
        content_area = QWidget()
        content_area.setStyleSheet(f"background-color: {CONTENT_BG};")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Header bar
        header_bar = QWidget()
        header_bar.setFixedHeight(64)
        header_bar.setStyleSheet(f"""
            background-color: {HEADER_BG};
            border-bottom: 1px solid {CARD_BORDER};
        """)
        header_bar_layout = QHBoxLayout()
        header_bar_layout.setContentsMargins(24, 0, 24, 0)

        self.page_title = QLabel("Attendance Records")
        self.page_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY};")
        header_bar_layout.addWidget(self.page_title)

        header_bar_layout.addStretch()

        self.date_label = QLabel()
        self.date_label.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY}; margin-right: 16px;")
        header_bar_layout.addWidget(self.date_label)

        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {PRIMARY};")
        header_bar_layout.addWidget(self.clock_label)

        header_bar.setLayout(header_bar_layout)
        content_layout.addWidget(header_bar)

        # Stacked Widget for pages
        self.pages = QStackedWidget()
        self.pages.setStyleSheet(f"background-color: {CONTENT_BG};")

        self.pages.addWidget(self._create_attendance_page())       # 0
        self.pages.addWidget(self._create_late_records_page())     # 1
        self.pages.addWidget(self._create_analytics_page())        # 2
        self.pages.addWidget(self._create_my_requests_page())      # 3
        self.pages.addWidget(self._create_reports_page())          # 4

        content_layout.addWidget(self.pages)
        content_area.setLayout(content_layout)
        root_layout.addWidget(content_area)

        self.setLayout(root_layout)

        # Set first nav button active
        self.nav_buttons[0].setChecked(True)
        self.update_clock()

    def _on_nav_clicked(self, clicked_btn):
        titles = ["Attendance Records", "Late Records", "Analytics", "My Requests", "Reports"]
        for i, btn in enumerate(self.nav_buttons):
            if btn == clicked_btn:
                btn.setChecked(True)
                self.pages.setCurrentIndex(i)
                self.page_title.setText(titles[i])
            else:
                btn.setChecked(False)

    # ===== PAGE BUILDERS =====

    def _create_attendance_page(self):
        """Attendance page: stats cards + action buttons + full attendance records"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Personal Stats Cards
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)

        self.status_card = StatCard("fa5s.info-circle", "Status", "N/A", WARNING)
        stats_grid.addWidget(self.status_card, 0, 0)

        self.paid_hours_card = StatCard("fa5s.hourglass-half", "Paid Hours", "0.00", PRIMARY)
        stats_grid.addWidget(self.paid_hours_card, 0, 1)

        self.late_count_card = StatCard("fa5s.exclamation-triangle", "Late Count", "0", DANGER)
        stats_grid.addWidget(self.late_count_card, 0, 2)

        layout.addLayout(stats_grid)

        # Attendance Action Buttons
        action_frame = QWidget()
        action_frame.setObjectName("actionFrame")
        action_frame.setStyleSheet(f"""
            QWidget#actionFrame {{
                background-color: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
            }}
        """)
        action_layout = QVBoxLayout()
        action_layout.setContentsMargins(20, 20, 20, 20)
        action_layout.setSpacing(16)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.checkin_btn = self._make_action_btn("fa5s.sign-in-alt", "Check In", SUCCESS)
        self.checkin_btn.clicked.connect(self.handle_check_in)
        btn_row.addWidget(self.checkin_btn)

        self.lunch_start_btn = self._make_action_btn("fa5s.utensils", "Start Lunch", WARNING)
        self.lunch_start_btn.clicked.connect(self.handle_start_lunch)
        btn_row.addWidget(self.lunch_start_btn)

        self.lunch_end_btn = self._make_action_btn("fa5s.utensils", "End Lunch", WARNING)
        self.lunch_end_btn.clicked.connect(self.handle_end_lunch)
        btn_row.addWidget(self.lunch_end_btn)

        self.checkout_btn = self._make_action_btn("fa5s.sign-out-alt", "Check Out", PRIMARY)
        self.checkout_btn.clicked.connect(self.handle_check_out)
        btn_row.addWidget(self.checkout_btn)

        btn_row.addStretch()

        ot_btn = self._make_action_btn("fa5s.business-time", "Request OT", "#F59E0B")
        ot_btn.clicked.connect(self.show_request_overtime_dialog)
        btn_row.addWidget(ot_btn)

        leave_btn = self._make_action_btn("fa5s.calendar-minus", "Request Leave", TEXT_SECONDARY)
        leave_btn.clicked.connect(self.show_request_leave_dialog)
        btn_row.addWidget(leave_btn)

        action_layout.addLayout(btn_row)
        action_frame.setLayout(action_layout)
        layout.addWidget(action_frame)

        # Full Attendance Records Table
        table_frame = QWidget()
        table_frame.setObjectName("attendTableFrame")
        table_frame.setStyleSheet(self._card_style("attendTableFrame"))
        table_inner = QVBoxLayout()
        table_inner.setContentsMargins(20, 20, 20, 20)
        table_inner.setSpacing(12)

        header_row = QHBoxLayout()
        title = QLabel("All Attendance Records")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        header_row.addWidget(title)
        header_row.addStretch()

        refresh_btn = self._make_action_btn("fa5s.sync-alt", "Refresh", PRIMARY)
        refresh_btn.clicked.connect(self.load_attendance_records)
        header_row.addWidget(refresh_btn)
        table_inner.addLayout(header_row)

        self.attendance_table_full = self._create_table(
            ["Date", "Time In", "Time Out", "Lunch Start", "Lunch End", "Total Time", "Lunch Duration", "Paid Hours", "OT Hours", "Status"]
        )
        table_inner.addWidget(self.attendance_table_full)

        table_frame.setLayout(table_inner)
        layout.addWidget(table_frame)

        container.setLayout(layout)
        scroll.setWidget(container)

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        page.setLayout(page_layout)
        return page

    def _create_late_records_page(self):
        """Late records filtered from attendance + late consideration request button"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Late summary cards
        summary_grid = QGridLayout()
        summary_grid.setSpacing(16)

        self.total_late_card = StatCard("fa5s.exclamation-triangle", "Total Late Days", "0", DANGER)
        summary_grid.addWidget(self.total_late_card, 0, 0)

        self.pending_late_card = StatCard("fa5s.clock", "Pending Considerations", "0", WARNING)
        summary_grid.addWidget(self.pending_late_card, 0, 1)

        self.approved_late_card = StatCard("fa5s.check-circle", "Approved Considerations", "0", SUCCESS)
        summary_grid.addWidget(self.approved_late_card, 0, 2)

        layout.addLayout(summary_grid)

        # Late records table
        late_frame = QWidget()
        late_frame.setObjectName("lateRecordsFrame")
        late_frame.setStyleSheet(self._card_style("lateRecordsFrame"))
        late_inner = QVBoxLayout()
        late_inner.setContentsMargins(20, 20, 20, 20)
        late_inner.setSpacing(12)

        late_header = QHBoxLayout()
        late_title = QLabel("Late Attendance Records")
        late_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        late_header.addWidget(late_title)
        late_header.addStretch()

        request_consideration_btn = self._make_action_btn("fa5s.hand-paper", "Request Late Consideration", WARNING)
        request_consideration_btn.clicked.connect(self.show_request_late_consideration_dialog)
        late_header.addWidget(request_consideration_btn)

        late_inner.addLayout(late_header)

        self.late_records_table = self._create_table(
            ["Date", "Time In", "Time Out", "Paid Hours", "Status"]
        )
        late_inner.addWidget(self.late_records_table)

        late_frame.setLayout(late_inner)
        layout.addWidget(late_frame)

        # Late consideration requests table
        consideration_frame = QWidget()
        consideration_frame.setObjectName("lateConsiderationFrame")
        consideration_frame.setStyleSheet(self._card_style("lateConsiderationFrame"))
        consideration_inner = QVBoxLayout()
        consideration_inner.setContentsMargins(20, 20, 20, 20)
        consideration_inner.setSpacing(12)

        consideration_header = QHBoxLayout()
        consideration_title = QLabel("Late Consideration Requests")
        consideration_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        consideration_header.addWidget(consideration_title)
        consideration_header.addStretch()

        consideration_filter = QComboBox()
        consideration_filter.addItems(["All", "Pending", "Approved", "Rejected"])
        consideration_filter.setFixedWidth(130)
        consideration_filter.setStyleSheet(self._combo_style())
        consideration_filter.currentTextChanged.connect(self._filter_late_considerations)
        self.late_consideration_filter = consideration_filter
        consideration_header.addWidget(consideration_filter)

        consideration_inner.addLayout(consideration_header)

        self.late_considerations_table = self._create_table(
            ["Date", "Reason", "Status", "Remarks", "Requested"]
        )
        self.late_considerations_table.setColumnWidth(1, 250)
        consideration_inner.addWidget(self.late_considerations_table)

        consideration_frame.setLayout(consideration_inner)
        layout.addWidget(consideration_frame)

        container.setLayout(layout)
        scroll.setWidget(container)

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        page.setLayout(page_layout)
        return page

    def _create_analytics_page(self):
        """Personal analytics with donut chart and bar chart"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Summary stats
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)

        self.total_days_card = StatCard("fa5s.calendar-check", "Total Days", "0", PRIMARY)
        stats_grid.addWidget(self.total_days_card, 0, 0)

        self.on_time_card = StatCard("fa5s.check-circle", "On Time", "0", SUCCESS)
        stats_grid.addWidget(self.on_time_card, 0, 1)

        self.late_analytics_card = StatCard("fa5s.exclamation-triangle", "Late", "0", DANGER)
        stats_grid.addWidget(self.late_analytics_card, 0, 2)

        self.avg_hours_card = StatCard("fa5s.hourglass-half", "Avg Hours/Day", "0.00", INFO)
        stats_grid.addWidget(self.avg_hours_card, 0, 3)

        layout.addLayout(stats_grid)

        # Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        # Donut chart - Today's Attendance
        donut_frame = QWidget()
        donut_frame.setObjectName("donutFrame")
        donut_frame.setStyleSheet(self._card_style("donutFrame"))
        donut_frame.setFixedHeight(360)
        donut_inner = QVBoxLayout()
        donut_inner.setContentsMargins(16, 12, 16, 12)
        donut_inner.setSpacing(4)

        donut_title = QLabel("Attendance Breakdown")
        donut_title.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {TEXT_PRIMARY};")
        donut_inner.addWidget(donut_title)

        self.donut_fig = Figure(figsize=(4, 3), dpi=100)
        self.donut_fig.patch.set_facecolor('#FFFFFF')
        self.donut_canvas = FigureCanvas(self.donut_fig)
        self.donut_canvas.setStyleSheet("background-color: #FFFFFF;")
        donut_inner.addWidget(self.donut_canvas, 1)

        donut_frame.setLayout(donut_inner)
        charts_row.addWidget(donut_frame, 1)

        # Stacked bar chart - Weekly Attendance Trend
        bar_frame = QWidget()
        bar_frame.setObjectName("barFrame")
        bar_frame.setStyleSheet(self._card_style("barFrame"))
        bar_frame.setFixedHeight(360)
        bar_inner = QVBoxLayout()
        bar_inner.setContentsMargins(16, 12, 16, 12)
        bar_inner.setSpacing(4)

        bar_title = QLabel("Weekly Attendance Trend")
        bar_title.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {TEXT_PRIMARY};")
        bar_inner.addWidget(bar_title)

        self.bar_fig = Figure(figsize=(6, 3), dpi=100)
        self.bar_fig.patch.set_facecolor('#FFFFFF')
        self.bar_canvas = FigureCanvas(self.bar_fig)
        self.bar_canvas.setStyleSheet("background-color: #FFFFFF;")
        bar_inner.addWidget(self.bar_canvas, 1)

        bar_frame.setLayout(bar_inner)
        charts_row.addWidget(bar_frame, 2)

        layout.addLayout(charts_row)

        # Monthly summary table
        monthly_frame = QWidget()
        monthly_frame.setObjectName("monthlyFrame")
        monthly_frame.setStyleSheet(self._card_style("monthlyFrame"))
        monthly_inner = QVBoxLayout()
        monthly_inner.setContentsMargins(20, 20, 20, 20)
        monthly_inner.setSpacing(12)

        monthly_title = QLabel("Monthly Summary (Last 6 Months)")
        monthly_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        monthly_inner.addWidget(monthly_title)

        self.monthly_table = self._create_table(
            ["Month", "Total Days", "On Time", "Late", "Total Paid Hours"]
        )
        monthly_inner.addWidget(self.monthly_table)

        monthly_frame.setLayout(monthly_inner)
        layout.addWidget(monthly_frame)

        container.setLayout(layout)
        scroll.setWidget(container)

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        page.setLayout(page_layout)
        return page

    def _create_my_requests_page(self):
        """My Requests page: leave and overtime requests"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # ── Leave Requests Section ──
        leave_frame = QWidget()
        leave_frame.setObjectName("leaveRequestsFrame")
        leave_frame.setStyleSheet(self._card_style("leaveRequestsFrame"))
        leave_layout = QVBoxLayout()
        leave_layout.setContentsMargins(20, 20, 20, 20)
        leave_layout.setSpacing(12)

        leave_header = QHBoxLayout()
        leave_title = QLabel("Leave Requests")
        leave_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        leave_header.addWidget(leave_title)
        leave_header.addStretch()

        request_leave_btn = self._make_action_btn("fa5s.plus", "New Request", PRIMARY)
        request_leave_btn.clicked.connect(self.show_request_leave_dialog)
        leave_header.addWidget(request_leave_btn)

        leave_filter = QComboBox()
        leave_filter.addItems(["All", "Pending", "Approved", "Rejected"])
        leave_filter.setFixedWidth(130)
        leave_filter.setStyleSheet(self._combo_style())
        leave_filter.currentTextChanged.connect(self._filter_leave_requests)
        self.leave_filter_combo = leave_filter
        leave_header.addWidget(leave_filter)

        leave_layout.addLayout(leave_header)

        self.leave_requests_table = self._create_table(
            ["Type", "Start Date", "End Date", "Days", "Reason", "Status", "Remarks", "Requested"]
        )
        self.leave_requests_table.setColumnWidth(4, 200)
        leave_layout.addWidget(self.leave_requests_table)

        leave_frame.setLayout(leave_layout)
        layout.addWidget(leave_frame)

        # ── Overtime Requests Section ──
        ot_frame = QWidget()
        ot_frame.setObjectName("otRequestsFrame")
        ot_frame.setStyleSheet(self._card_style("otRequestsFrame"))
        ot_layout = QVBoxLayout()
        ot_layout.setContentsMargins(20, 20, 20, 20)
        ot_layout.setSpacing(12)

        ot_header = QHBoxLayout()
        ot_title = QLabel("Overtime Requests")
        ot_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        ot_header.addWidget(ot_title)
        ot_header.addStretch()

        request_ot_btn = self._make_action_btn("fa5s.plus", "New Request", WARNING)
        request_ot_btn.clicked.connect(self.show_request_overtime_dialog)
        ot_header.addWidget(request_ot_btn)

        ot_filter = QComboBox()
        ot_filter.addItems(["All", "Pending", "Approved", "Rejected"])
        ot_filter.setFixedWidth(130)
        ot_filter.setStyleSheet(self._combo_style())
        ot_filter.currentTextChanged.connect(self._filter_ot_requests)
        self.ot_filter_combo = ot_filter
        ot_header.addWidget(ot_filter)

        ot_layout.addLayout(ot_header)

        self.ot_requests_table = self._create_table(
            ["Date", "Hours", "Reason", "Status", "Remarks", "Requested"]
        )
        self.ot_requests_table.setColumnWidth(2, 200)
        ot_layout.addWidget(self.ot_requests_table)

        ot_frame.setLayout(ot_layout)
        layout.addWidget(ot_frame)

        layout.addStretch()

        container.setLayout(layout)
        scroll.setWidget(container)

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        page.setLayout(page_layout)
        return page

    def _create_reports_page(self):
        """Reports page: personal attendance report export"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        reports_frame = QWidget()
        reports_frame.setObjectName("reportsFrame")
        reports_frame.setStyleSheet(self._card_style("reportsFrame"))
        reports_inner = QVBoxLayout()
        reports_inner.setContentsMargins(20, 20, 20, 20)
        reports_inner.setSpacing(20)

        reports_title = QLabel("Export My Reports")
        reports_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        reports_inner.addWidget(reports_title)

        form = QFormLayout()
        form.setSpacing(12)

        self.report_type = QComboBox()
        self.report_type.addItems(["My Attendance Report", "My Late Report", "My Requests Summary"])
        self.report_type.setStyleSheet(self._combo_style())
        form.addRow("Report Type:", self.report_type)

        date_row = QHBoxLayout()
        self.report_start_date = QDateEdit()
        self.report_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.report_start_date.setCalendarPopup(True)
        self.report_start_date.setStyleSheet(self._date_edit_style())
        date_row.addWidget(QLabel("From:"))
        date_row.addWidget(self.report_start_date)

        self.report_end_date = QDateEdit()
        self.report_end_date.setDate(QDate.currentDate())
        self.report_end_date.setCalendarPopup(True)
        self.report_end_date.setStyleSheet(self._date_edit_style())
        date_row.addWidget(QLabel("To:"))
        date_row.addWidget(self.report_end_date)
        date_row.addStretch()

        form.addRow("Date Range:", date_row)

        reports_inner.addLayout(form)

        export_row = QHBoxLayout()
        export_row.setSpacing(12)

        pdf_btn = self._make_action_btn("fa5s.file-pdf", "Export PDF", DANGER)
        pdf_btn.clicked.connect(self.export_to_pdf)
        export_row.addWidget(pdf_btn)

        export_row.addStretch()
        reports_inner.addLayout(export_row)

        reports_inner.addStretch()

        reports_frame.setLayout(reports_inner)
        layout.addWidget(reports_frame)
        layout.addStretch()

        page.setLayout(layout)
        return page

    # ===== HELPER WIDGETS =====

    def _card_style(self, object_name):
        return f"""
            QWidget#{object_name} {{
                background-color: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
            }}
            QWidget#{object_name} QLabel {{
                background-color: {CARD_BG};
                border: none;
            }}
        """

    def _combo_style(self):
        return f"""
            QComboBox {{
                padding: 6px 12px;
                border: 1px solid {CARD_BORDER};
                border-radius: 6px;
                font-size: 12px;
                color: {TEXT_PRIMARY};
                background-color: white;
            }}
        """

    def _date_edit_style(self):
        return f"""
            QDateEdit {{
                padding: 6px 12px;
                border: 1px solid {CARD_BORDER};
                border-radius: 6px;
                font-size: 12px;
                color: {TEXT_PRIMARY};
                background-color: white;
            }}
        """

    def _make_action_btn(self, icon_name, text, color):
        btn = QPushButton(f"  {text}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(40)
        try:
            btn.setIcon(qta.icon(icon_name, color="white"))
            btn.setIconSize(QSize(16, 16))
        except Exception:
            pass

        text_color = "#333333" if color == "#FFD107" else "white"

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
            }}
            QPushButton:disabled {{
                background-color: #CBD5E1;
                color: #94A3B8;
            }}
        """)
        return btn

    def _create_table(self, headers):
        table = CenteredTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: 10px;
                outline: none;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px 0px;
                color: {TEXT_PRIMARY};
                border-bottom: 1px solid #F1F5F9;
            }}
            QTableWidget::item:selected {{
                background-color: #EFF6FF;
                color: {TEXT_PRIMARY};
            }}
            QTableWidget::item:alternate {{
                background-color: #F8FAFC;
            }}
            QHeaderView::section {{
                background-color: #F8FAFC;
                color: {TEXT_SECONDARY};
                padding: 8px 0px;
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
                border: none;
                border-bottom: 2px solid {CARD_BORDER};
            }}
            QScrollBar:vertical {{
                background: #F8FAFC;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: #CBD5E1;
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #94A3B8;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setMinimumSectionSize(100)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        table.verticalHeader().setDefaultSectionSize(44)
        return table

    # ===== DATA LOADING =====

    def update_clock(self):
        now = datetime.now()
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))
        self.clock_label.setText(now.strftime("%I:%M:%S %p"))

    def load_data(self):
        self.load_attendance_records()
        self.load_late_records()
        self.load_analytics()
        self.load_my_requests()

    def load_attendance_records(self):
        """Load attendance stats and full attendance records"""
        today_record = self.attendance_controller.get_today_attendance()

        if today_record:
            status = today_record.get('status', 'N/A')
            status_color = WARNING if 'Late' in status else SUCCESS
            self.status_card.set_value(status, status_color)
            paid_hours = float(today_record.get('paid_hours') or 0)
            self.paid_hours_card.set_value(f"{paid_hours:.2f}", PRIMARY)
        else:
            self.status_card.set_value("N/A", TEXT_MUTED)
            self.paid_hours_card.set_value("0.00", TEXT_MUTED)

        self.update_button_states(today_record)

        # Late count
        late_records = self.dashboard_controller.get_employee_late_records(self.employee_id) or []
        self.late_count_card.set_value(str(len(late_records)), DANGER if late_records else SUCCESS)

        # Full attendance records
        records = self.dashboard_controller.get_my_attendance_records(limit=100)
        self._populate_attendance_table_full(self.attendance_table_full, records)

    def load_late_records(self):
        """Load late-only attendance records and late consideration data"""
        late_records = self.dashboard_controller.get_employee_late_records(self.employee_id) or []
        self.total_late_card.set_value(str(len(late_records)))

        # Populate late records table
        self.late_records_table.setRowCount(len(late_records))
        for row, record in enumerate(late_records):
            self.late_records_table.setItem(row, 0, QTableWidgetItem(str(record.get('date', '-'))))
            self.late_records_table.setItem(row, 1, QTableWidgetItem(self.dashboard_controller.format_time(record.get('time_in'))))
            self.late_records_table.setItem(row, 2, QTableWidgetItem(self.dashboard_controller.format_time(record.get('time_out'))))
            self.late_records_table.setItem(row, 3, QTableWidgetItem(self.dashboard_controller.format_hours(record.get('paid_hours'))))

            status_item = QTableWidgetItem(str(record.get('status', '-')))
            status_item.setForeground(QBrush(QColor(DANGER)))
            status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.late_records_table.setItem(row, 4, status_item)

        # Load late considerations
        self._all_late_considerations = self.dashboard_controller.get_employee_late_considerations(self.employee_id) or []
        pending_count = sum(1 for r in self._all_late_considerations if r.get('status') == 'Pending')
        approved_count = sum(1 for r in self._all_late_considerations if r.get('status') == 'Approved')
        self.pending_late_card.set_value(str(pending_count))
        self.approved_late_card.set_value(str(approved_count))

        current_filter = self.late_consideration_filter.currentText() if hasattr(self, 'late_consideration_filter') else "All"
        self._filter_late_considerations(current_filter)

    def load_analytics(self):
        """Load analytics data and update charts"""
        stats = self.dashboard_controller.get_employee_stats(self.employee_id)
        if stats:
            self.total_days_card.set_value(str(stats.get('total_days', 0)))
            self.on_time_card.set_value(str(stats.get('on_time_days', 0)))
            self.late_analytics_card.set_value(str(stats.get('late_days', 0)))
            avg_hours = stats.get('avg_paid_hours', 0)
            self.avg_hours_card.set_value(f"{float(avg_hours):.2f}" if avg_hours else "0.00")

            on_time = int(stats.get('on_time_days', 0) or 0)
            late = int(stats.get('late_days', 0) or 0)
            self._update_donut_chart(on_time, late)
        else:
            self._update_donut_chart(0, 0)

        self._update_bar_chart()
        self._load_monthly_summary()

    def load_my_requests(self):
        """Load leave and overtime requests"""
        self._all_leave_requests = self.dashboard_controller.get_employee_leaves(self.employee_id) or []
        self._all_ot_requests = self.dashboard_controller.get_employee_overtime_requests(self.employee_id) or []

        leave_filter = self.leave_filter_combo.currentText() if hasattr(self, 'leave_filter_combo') else "All"
        ot_filter = self.ot_filter_combo.currentText() if hasattr(self, 'ot_filter_combo') else "All"
        self._filter_leave_requests(leave_filter)
        self._filter_ot_requests(ot_filter)

    # ===== TABLE POPULATION =====

    def _populate_attendance_table_full(self, table, records):
        """Populate full attendance table with all columns"""
        table.setRowCount(len(records))
        for row, record in enumerate(records):
            table.setItem(row, 0, QTableWidgetItem(str(record.get('date', '-'))))
            table.setItem(row, 1, QTableWidgetItem(self.dashboard_controller.format_time(record.get('time_in'))))
            table.setItem(row, 2, QTableWidgetItem(self.dashboard_controller.format_time(record.get('time_out'))))
            table.setItem(row, 3, QTableWidgetItem(self.dashboard_controller.format_time(record.get('lunch_start'))))
            table.setItem(row, 4, QTableWidgetItem(self.dashboard_controller.format_time(record.get('lunch_end'))))
            table.setItem(row, 5, QTableWidgetItem(self.dashboard_controller.format_hours(record.get('total_time'))))
            table.setItem(row, 6, QTableWidgetItem(self.dashboard_controller.format_hours(record.get('lunch_duration'))))
            table.setItem(row, 7, QTableWidgetItem(self.dashboard_controller.format_hours(record.get('paid_hours'))))
            ot = record.get('overtime_hours', 0)
            table.setItem(row, 8, QTableWidgetItem(self.dashboard_controller.format_hours(ot) if ot else "0.00"))

            status = str(record.get('status', '-'))
            status_item = QTableWidgetItem(status)
            if 'Late' in status:
                status_item.setForeground(QBrush(QColor(DANGER)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            elif 'On Time' in status:
                status_item.setForeground(QBrush(QColor(SUCCESS)))
            table.setItem(row, 9, status_item)

    # ===== CHARTS =====

    def _update_donut_chart(self, on_time, late):
        """Render a donut chart showing personal attendance breakdown."""
        self.donut_fig.clear()
        ax = self.donut_fig.add_subplot(111)

        values = [on_time, late]
        labels = ['On-Time', 'Late']
        colors = [SUCCESS, WARNING]

        # Filter out zero slices
        filtered = [(v, l, c) for v, l, c in zip(values, labels, colors) if v > 0]

        if not filtered:
            # Show an empty gray donut ring with "0 Records" text
            ax.pie([1], colors=['#E2E8F0'], startangle=90,
                   wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
            ax.text(0, 0, '0 Records', ha='center', va='center',
                    fontsize=12, color=TEXT_MUTED, fontweight='500')
        else:
            vals, lbls, cols = zip(*filtered)
            wedges, texts, autotexts = ax.pie(
                vals, labels=lbls, colors=cols, autopct='%1.0f%%',
                startangle=90, pctdistance=0.78,
                wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
                textprops={'fontsize': 10, 'color': TEXT_PRIMARY, 'weight': '500'}
            )
            for t in autotexts:
                t.set_fontsize(9)
                t.set_color('white')
                t.set_fontweight('bold')

        ax.set_aspect('equal')
        self.donut_fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        self.donut_canvas.draw()

    def _update_bar_chart(self):
        """Render a stacked bar chart showing the last 7 days attendance trend."""
        summary = self.dashboard_controller.get_weekly_attendance_summary()

        self.bar_fig.clear()
        ax = self.bar_fig.add_subplot(111)

        if summary:
            dates = [row['date'].strftime('%a\n%m/%d') if hasattr(row['date'], 'strftime')
                     else str(row['date']) for row in summary]
            on_time_vals = [row['present_count'] - row['late_count'] for row in summary]
            late_vals = [row['late_count'] for row in summary]

            x = range(len(dates))
            bar_width = 0.55

            ax.bar(x, on_time_vals, bar_width, label='On-Time', color=SUCCESS, edgecolor='white', linewidth=0.5)
            ax.bar(x, late_vals, bar_width, bottom=on_time_vals, label='Late', color=WARNING, edgecolor='white', linewidth=0.5)

            ax.set_xticks(x)
            ax.set_xticklabels(dates, fontsize=8, color=TEXT_SECONDARY)
            ax.set_ylabel('Employees', fontsize=9, color=TEXT_SECONDARY)
            ax.legend(fontsize=8, loc='upper right', framealpha=0.9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(CARD_BORDER)
            ax.spines['bottom'].set_color(CARD_BORDER)
            ax.tick_params(axis='y', labelsize=8, colors=TEXT_SECONDARY)
            ax.set_axisbelow(True)
            ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                    fontsize=13, color=TEXT_SECONDARY, transform=ax.transAxes)
            ax.axis('off')

        self.bar_fig.subplots_adjust(left=0.08, right=0.97, top=0.92, bottom=0.12)
        self.bar_canvas.draw()

    def _load_monthly_summary(self):
        """Load monthly summary data into table"""
        data = self.dashboard_controller.get_employee_monthly_summary(self.employee_id) or []
        self.monthly_table.setRowCount(len(data))
        for row, record in enumerate(data):
            self.monthly_table.setItem(row, 0, QTableWidgetItem(str(record.get('month', '-'))))
            self.monthly_table.setItem(row, 1, QTableWidgetItem(str(record.get('total_days', 0))))
            self.monthly_table.setItem(row, 2, QTableWidgetItem(str(record.get('on_time_days', 0))))

            late_days = int(record.get('late_days', 0) or 0)
            late_item = QTableWidgetItem(str(late_days))
            if late_days > 0:
                late_item.setForeground(QBrush(QColor(DANGER)))
                late_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.monthly_table.setItem(row, 3, late_item)

            total_hours = float(record.get('total_paid_hours', 0) or 0)
            self.monthly_table.setItem(row, 4, QTableWidgetItem(f"{total_hours:.2f}"))

    # ===== FILTER METHODS =====

    def _filter_leave_requests(self, status):
        if not hasattr(self, '_all_leave_requests'):
            return
        filtered = self._all_leave_requests if status == "All" else [r for r in self._all_leave_requests if r.get('status') == status]
        self._populate_leave_requests_table(filtered)

    def _filter_ot_requests(self, status):
        if not hasattr(self, '_all_ot_requests'):
            return
        filtered = self._all_ot_requests if status == "All" else [r for r in self._all_ot_requests if r.get('status') == status]
        self._populate_ot_requests_table(filtered)

    def _filter_late_considerations(self, status):
        if not hasattr(self, '_all_late_considerations'):
            return
        filtered = self._all_late_considerations if status == "All" else [r for r in self._all_late_considerations if r.get('status') == status]
        self._populate_late_considerations_table(filtered)

    def _populate_leave_requests_table(self, records):
        self.leave_requests_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.leave_requests_table.setItem(row, 0, QTableWidgetItem(str(record.get('leave_type', '-'))))
            self.leave_requests_table.setItem(row, 1, QTableWidgetItem(str(record.get('start_date', '-'))))
            self.leave_requests_table.setItem(row, 2, QTableWidgetItem(str(record.get('end_date', '-'))))
            self.leave_requests_table.setItem(row, 3, QTableWidgetItem(str(record.get('days_count', '-'))))
            reason = str(record.get('reason', '-'))
            if len(reason) > 50:
                reason = reason[:50] + "..."
            self.leave_requests_table.setItem(row, 4, QTableWidgetItem(reason))

            status = str(record.get('status', '-'))
            status_item = QTableWidgetItem(status)
            if status == 'Approved':
                status_item.setForeground(QBrush(QColor(SUCCESS)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            elif status == 'Rejected':
                status_item.setForeground(QBrush(QColor(DANGER)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            elif status == 'Pending':
                status_item.setForeground(QBrush(QColor(WARNING)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.leave_requests_table.setItem(row, 5, status_item)

            self.leave_requests_table.setItem(row, 6, QTableWidgetItem(str(record.get('remarks', '') or '-')))

            requested_at = record.get('requested_at', '-')
            if hasattr(requested_at, 'strftime'):
                requested_at = requested_at.strftime('%Y-%m-%d %I:%M %p')
            self.leave_requests_table.setItem(row, 7, QTableWidgetItem(str(requested_at)))

    def _populate_ot_requests_table(self, records):
        self.ot_requests_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.ot_requests_table.setItem(row, 0, QTableWidgetItem(str(record.get('request_date', '-'))))
            hours = record.get('hours_requested', '-')
            self.ot_requests_table.setItem(row, 1, QTableWidgetItem(f"{hours}" if hours != '-' else '-'))
            reason = str(record.get('reason', '-'))
            if len(reason) > 50:
                reason = reason[:50] + "..."
            self.ot_requests_table.setItem(row, 2, QTableWidgetItem(reason))

            status = str(record.get('status', '-'))
            status_item = QTableWidgetItem(status)
            if status == 'Approved':
                status_item.setForeground(QBrush(QColor(SUCCESS)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            elif status == 'Rejected':
                status_item.setForeground(QBrush(QColor(DANGER)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            elif status == 'Pending':
                status_item.setForeground(QBrush(QColor(WARNING)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.ot_requests_table.setItem(row, 3, status_item)

            self.ot_requests_table.setItem(row, 4, QTableWidgetItem(str(record.get('remarks', '') or '-')))

            created_at = record.get('created_at', '-')
            if hasattr(created_at, 'strftime'):
                created_at = created_at.strftime('%Y-%m-%d %I:%M %p')
            self.ot_requests_table.setItem(row, 5, QTableWidgetItem(str(created_at)))

    def _populate_late_considerations_table(self, records):
        self.late_considerations_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.late_considerations_table.setItem(row, 0, QTableWidgetItem(str(record.get('attendance_date', '-'))))

            reason = str(record.get('reason', '-'))
            if len(reason) > 60:
                reason = reason[:60] + "..."
            self.late_considerations_table.setItem(row, 1, QTableWidgetItem(reason))

            status = str(record.get('status', '-'))
            status_item = QTableWidgetItem(status)
            if status == 'Approved':
                status_item.setForeground(QBrush(QColor(SUCCESS)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            elif status == 'Rejected':
                status_item.setForeground(QBrush(QColor(DANGER)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            elif status == 'Pending':
                status_item.setForeground(QBrush(QColor(WARNING)))
                status_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.late_considerations_table.setItem(row, 2, status_item)

            self.late_considerations_table.setItem(row, 3, QTableWidgetItem(str(record.get('remarks', '') or '-')))

            created_at = record.get('created_at', '-')
            if hasattr(created_at, 'strftime'):
                created_at = created_at.strftime('%Y-%m-%d %I:%M %p')
            self.late_considerations_table.setItem(row, 4, QTableWidgetItem(str(created_at)))

    # ===== BUTTON STATES =====

    def update_button_states(self, today_record):
        if not today_record:
            self.checkin_btn.setEnabled(True)
            self.lunch_start_btn.setEnabled(False)
            self.lunch_end_btn.setEnabled(False)
            self.checkout_btn.setEnabled(False)
        else:
            time_out = today_record.get('time_out')
            lunch_start = today_record.get('lunch_start')
            lunch_end = today_record.get('lunch_end')

            if time_out:
                self.checkin_btn.setEnabled(False)
                self.lunch_start_btn.setEnabled(False)
                self.lunch_end_btn.setEnabled(False)
                self.checkout_btn.setEnabled(False)
            elif lunch_start and not lunch_end:
                self.checkin_btn.setEnabled(False)
                self.lunch_start_btn.setEnabled(False)
                self.lunch_end_btn.setEnabled(True)
                self.checkout_btn.setEnabled(False)
            elif lunch_start and lunch_end:
                self.checkin_btn.setEnabled(False)
                self.lunch_start_btn.setEnabled(False)
                self.lunch_end_btn.setEnabled(False)
                self.checkout_btn.setEnabled(True)
            else:
                self.checkin_btn.setEnabled(False)
                self.lunch_start_btn.setEnabled(True)
                self.lunch_end_btn.setEnabled(False)
                self.checkout_btn.setEnabled(True)

    # ===== ATTENDANCE ACTIONS =====

    def handle_check_in(self):
        can, title, message, msg_type = self.attendance_controller.can_check_in()
        if not can:
            show_message(self, title, message, msg_type)
            return
        if not show_question(self, "Confirm Check-In",
                f"Are you sure you want to check in now?\n\n"
                f"Time: {datetime.now().strftime('%I:%M %p')}"):
            return
        success, title, message, msg_type = self.attendance_controller.check_in()
        show_message(self, title, message, msg_type)
        if success:
            self.load_attendance_records()

    def handle_start_lunch(self):
        can, title, message, msg_type = self.attendance_controller.can_start_lunch()
        if not can:
            show_message(self, title, message, msg_type)
            return
        success, title, message, msg_type = self.attendance_controller.start_lunch()
        show_message(self, title, message, msg_type)
        if success:
            self.load_attendance_records()

    def handle_end_lunch(self):
        can, title, message, msg_type = self.attendance_controller.can_end_lunch()
        if not can:
            show_message(self, title, message, msg_type)
            return
        success, title, message, msg_type = self.attendance_controller.end_lunch()
        show_message(self, title, message, msg_type)
        if success:
            self.load_attendance_records()

    def handle_check_out(self):
        can, title, message, msg_type = self.attendance_controller.can_check_out()
        if not can:
            show_message(self, title, message, msg_type)
            return
        success, title, message, msg_type = self.attendance_controller.check_out()
        show_message(self, title, message, msg_type)
        if success:
            self.load_attendance_records()
            self.load_late_records()
            self.load_analytics()

    def show_change_password_dialog(self):
        dialog = ChangePasswordDialog(self.user_data, self)
        dialog.exec()

    def handle_logout(self):
        today_record = self.attendance_controller.get_today_record()
        is_checked_in = today_record and today_record.get('time_in') and not today_record.get('time_out')

        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Logout")
        dialog.setModal(True)
        dialog.setMinimumWidth(420)
        dialog.setStyleSheet(f"background-color: {CARD_BG};")

        layout = QVBoxLayout()

        if is_checked_in:
            message = QLabel(
                f"<h3 style='color: {WARNING};'>You're Still Checked In!</h3>"
                "<p>You haven't checked out yet. What would you like to do?</p>"
            )
        else:
            message = QLabel(
                "<h3>Confirm Logout</h3>"
                "<p>Are you sure you want to logout?</p>"
            )
        message.setWordWrap(True)
        message.setStyleSheet("padding: 20px;")
        layout.addWidget(message)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = self._make_action_btn("fa5s.times", "Cancel", TEXT_SECONDARY)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        if is_checked_in:
            checkout_btn = self._make_action_btn("fa5s.sign-out-alt", "Check Out & Logout", SUCCESS)
            checkout_btn.clicked.connect(lambda: self._checkout_and_logout(dialog))
            button_layout.addWidget(checkout_btn)

            logout_only_btn = self._make_action_btn("fa5s.sign-out-alt", "Logout Only", WARNING)
            logout_only_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(logout_only_btn)
        else:
            yes_btn = self._make_action_btn("fa5s.check", "Yes, Logout", PRIMARY)
            yes_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(yes_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.finished.emit()
            self.close()

    def _checkout_and_logout(self, dialog):
        success, title, message, msg_type = self.attendance_controller.check_out()
        show_message(self, title, message, msg_type)
        if success:
            dialog.accept()

    # ===== NOTIFICATIONS =====

    def _check_notifications(self):
        """Check for unnotified leave/OT/late consideration request reviews."""
        unnotified_leaves = self.dashboard_controller.get_unnotified_leave_reviews(self.employee_id) or []
        unnotified_ot = self.dashboard_controller.get_unnotified_overtime_reviews(self.employee_id) or []
        unnotified_late = self.dashboard_controller.get_unnotified_late_consideration_reviews(self.employee_id) or []

        total_unnotified = len(unnotified_leaves) + len(unnotified_ot) + len(unnotified_late)

        # Update nav badge for My Requests
        if total_unnotified > 0 and len(self.nav_buttons) >= 4:
            my_requests_btn = self.nav_buttons[3]
            my_requests_btn.setText(f"  My Requests  ({total_unnotified})")

        if total_unnotified == 0:
            return

        # Build notification message
        lines = []
        for leave in unnotified_leaves:
            status = leave.get('status', '')
            leave_type = leave.get('leave_type', '')
            start = leave.get('start_date', '')
            end = leave.get('end_date', '')
            remarks = leave.get('remarks', '') or ''
            color = SUCCESS if status == 'Approved' else DANGER
            icon_char = '\u2705' if status == 'Approved' else '\u274c'
            line = f"{icon_char} <b>Leave {status}</b> \u2014 {leave_type} ({start} to {end})"
            if remarks:
                line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;<i>Remarks: {remarks}</i>"
            lines.append(f"<p style='margin: 8px 0; padding: 10px; background: {color}10; border-left: 4px solid {color}; border-radius: 4px;'>{line}</p>")

        for ot in unnotified_ot:
            status = ot.get('status', '')
            req_date = ot.get('request_date', '')
            hours = ot.get('hours_requested', '')
            remarks = ot.get('remarks', '') or ''
            color = SUCCESS if status == 'Approved' else DANGER
            icon_char = '\u2705' if status == 'Approved' else '\u274c'
            line = f"{icon_char} <b>Overtime {status}</b> \u2014 {req_date} ({hours} hrs)"
            if remarks:
                line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;<i>Remarks: {remarks}</i>"
            lines.append(f"<p style='margin: 8px 0; padding: 10px; background: {color}10; border-left: 4px solid {color}; border-radius: 4px;'>{line}</p>")

        for lc in unnotified_late:
            status = lc.get('status', '')
            att_date = lc.get('attendance_date', '')
            remarks = lc.get('remarks', '') or ''
            color = SUCCESS if status == 'Approved' else DANGER
            icon_char = '\u2705' if status == 'Approved' else '\u274c'
            line = f"{icon_char} <b>Late Consideration {status}</b> \u2014 {att_date}"
            if remarks:
                line += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;<i>Remarks: {remarks}</i>"
            lines.append(f"<p style='margin: 8px 0; padding: 10px; background: {color}10; border-left: 4px solid {color}; border-radius: 4px;'>{line}</p>")

        # Show notification dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Request Updates")
        dialog.setModal(True)
        dialog.setMinimumWidth(520)
        dialog.setMaximumHeight(500)
        dialog.setStyleSheet(f"background-color: {CARD_BG};")

        dlg_layout = QVBoxLayout()
        dlg_layout.setContentsMargins(24, 24, 24, 24)
        dlg_layout.setSpacing(16)

        header = QLabel(f"<h2 style='color: {PRIMARY}; margin: 0;'>\U0001f4cb Request Updates</h2>"
                        f"<p style='color: {TEXT_SECONDARY}; margin-top: 4px;'>You have {total_unnotified} new update(s) on your requests</p>")
        header.setWordWrap(True)
        dlg_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setMaximumHeight(320)

        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        for line_html in lines:
            lbl = QLabel(line_html)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("border: none;")
            content_layout.addWidget(lbl)

        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        dlg_layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = self._make_action_btn("fa5s.check", "Got it", PRIMARY)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        dlg_layout.addLayout(btn_layout)

        dialog.setLayout(dlg_layout)
        dialog.exec()

        # Mark all as notified
        self.dashboard_controller.mark_all_leaves_notified(self.employee_id)
        self.dashboard_controller.mark_all_overtime_notified(self.employee_id)
        self.dashboard_controller.mark_all_late_considerations_notified(self.employee_id)

        # Reset badge
        if len(self.nav_buttons) >= 4:
            self.nav_buttons[3].setText("  My Requests")

    # ===== LATE CONSIDERATION REQUEST =====

    def show_request_late_consideration_dialog(self):
        """Show dialog to request late consideration for a specific date"""
        late_records = self.dashboard_controller.get_employee_late_records(self.employee_id) or []
        if not late_records:
            show_info(self, "No Late Records", "You don't have any late attendance records.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Request Late Consideration")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(f"background-color: {CARD_BG};")

        layout = QVBoxLayout()

        info_label = QLabel(
            f"<h3>Request Late Consideration</h3>"
            f"<p>Select a date when you were late and provide a reason for consideration.</p>"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"padding: 12px; background-color: #FEF3C7; border-radius: 8px; border-left: 4px solid {WARNING};")
        layout.addWidget(info_label)

        form_layout = QFormLayout()

        # Date combo showing late dates
        date_combo = QComboBox()
        existing_considerations = self.dashboard_controller.get_employee_late_considerations(self.employee_id) or []
        existing_dates = set(str(r.get('attendance_date', '')) for r in existing_considerations)

        for record in late_records:
            d = str(record.get('date', ''))
            if d and d not in existing_dates:
                time_in = self.dashboard_controller.format_time(record.get('time_in'))
                date_combo.addItem(f"{d}  (Checked in: {time_in})", d)

        if date_combo.count() == 0:
            show_info(self, "No Eligible Dates",
                      "All your late dates already have consideration requests submitted.")
            dialog.close()
            return

        form_layout.addRow("Late Date:", date_combo)

        from PyQt6.QtWidgets import QTextEdit
        reason_edit = QTextEdit()
        reason_edit.setPlaceholderText("Explain why you were late (e.g., traffic, emergency, etc.)...")
        reason_edit.setMaximumHeight(100)
        form_layout.addRow("Reason:", reason_edit)

        # Evidence attachment
        evidence_path = [None]
        evidence_row = QHBoxLayout()
        evidence_label = QLabel("No file selected")
        evidence_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(100)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #2563EB;
            }}
        """)

        def browse_evidence():
            file_path, _ = QFileDialog.getOpenFileName(
                dialog, "Select Evidence File", "",
                "Images & Documents (*.png *.jpg *.jpeg *.gif *.bmp *.pdf *.doc *.docx);;All Files (*.*)"
            )
            if file_path:
                evidence_path[0] = file_path
                fname = os.path.basename(file_path)
                evidence_label.setText(fname)
                evidence_label.setStyleSheet(f"color: {PRIMARY}; font-size: 12px; font-weight: bold;")

        browse_btn.clicked.connect(browse_evidence)
        evidence_row.addWidget(evidence_label, 1)
        evidence_row.addWidget(browse_btn)
        form_layout.addRow("Evidence:", evidence_row)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = self._make_action_btn("fa5s.times", "Cancel", TEXT_SECONDARY)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        submit_btn = self._make_action_btn("fa5s.paper-plane", "Submit Request", WARNING)

        def submit_consideration():
            selected_date = date_combo.currentData()
            reason = reason_edit.toPlainText().strip()

            if not reason:
                show_warning(dialog, "Missing Reason", "Please provide a reason for your late consideration request.")
                return

            # Copy evidence file
            saved_evidence_path = None
            if evidence_path[0]:
                import shutil
                evidence_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "evidence")
                os.makedirs(evidence_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = os.path.splitext(evidence_path[0])[1]
                dest_filename = f"late_{self.employee_id}_{timestamp}{ext}"
                dest_path = os.path.join(evidence_dir, dest_filename)
                try:
                    shutil.copy2(evidence_path[0], dest_path)
                    saved_evidence_path = dest_filename
                except Exception:
                    pass

            if self.dashboard_controller.create_late_consideration(
                    self.employee_id, selected_date, reason, saved_evidence_path):
                show_info(dialog, "Success",
                          f"Late consideration request submitted!\nDate: {selected_date}\nPending admin approval.")
                dialog.accept()
                self.load_late_records()
                self.load_my_requests()
            else:
                show_error(dialog, "Error", "Failed to submit late consideration request. You may already have a request for this date.")

        submit_btn.clicked.connect(submit_consideration)
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()

    # ===== LEAVE/OVERTIME REQUESTS =====

    def show_request_leave_dialog(self):
        from PyQt6.QtWidgets import QTextEdit

        employee = self.dashboard_controller.get_employee_by_id(self.employee_id)
        if not employee:
            show_error(self, "Error", "Could not load employee information.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Request Leave")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(f"background-color: {CARD_BG};")

        layout = QVBoxLayout()

        info_label = QLabel(
            f"<h3>Request Leave</h3>"
            f"<p><b>Employee:</b> {employee.get('full_name')}<br>"
            f"<b>Available Leave Credits:</b> {employee.get('leave_credits', 0)} days</p>"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"padding: 12px; background-color: {PRIMARY}10; border-radius: 8px; border-left: 4px solid {PRIMARY};")
        layout.addWidget(info_label)

        form_layout = QFormLayout()

        leave_type_combo = QComboBox()
        leave_type_combo.addItems(["Sick Leave", "Vacation Leave", "Emergency Leave", "Personal Leave"])
        form_layout.addRow("Leave Type:", leave_type_combo)

        start_date_edit = QDateEdit()
        start_date_edit.setDate(QDate.currentDate())
        start_date_edit.setCalendarPopup(True)
        start_date_edit.setMinimumDate(QDate.currentDate())
        form_layout.addRow("Start Date:", start_date_edit)

        end_date_edit = QDateEdit()
        end_date_edit.setDate(QDate.currentDate())
        end_date_edit.setCalendarPopup(True)
        end_date_edit.setMinimumDate(QDate.currentDate())
        form_layout.addRow("End Date:", end_date_edit)

        days_label = QLabel("1 day(s)")
        days_label.setStyleSheet(f"font-weight: bold; color: {PRIMARY};")
        form_layout.addRow("Total Days:", days_label)

        def update_days_count():
            start = start_date_edit.date().toPyDate()
            end = end_date_edit.date().toPyDate()
            days = (end - start).days + 1
            if days < 1:
                days = 1
                end_date_edit.setDate(start_date_edit.date())
            days_label.setText(f"{days} day(s)")
            if days > employee.get('leave_credits', 0):
                days_label.setStyleSheet(f"font-weight: bold; color: {DANGER};")
                days_label.setText(f"{days} day(s) - Insufficient leave credits!")
            else:
                days_label.setStyleSheet(f"font-weight: bold; color: {PRIMARY};")

        start_date_edit.dateChanged.connect(update_days_count)
        end_date_edit.dateChanged.connect(update_days_count)

        reason_edit = QTextEdit()
        reason_edit.setPlaceholderText("Enter reason for leave request...")
        reason_edit.setMaximumHeight(100)
        form_layout.addRow("Reason:", reason_edit)

        # Evidence attachment
        evidence_path = [None]
        evidence_row = QHBoxLayout()
        evidence_label = QLabel("No file selected")
        evidence_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(100)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #2563EB;
            }}
        """)

        def browse_evidence():
            file_path, _ = QFileDialog.getOpenFileName(
                dialog, "Select Evidence File", "",
                "Images & Documents (*.png *.jpg *.jpeg *.gif *.bmp *.pdf *.doc *.docx);;All Files (*.*)"
            )
            if file_path:
                evidence_path[0] = file_path
                fname = os.path.basename(file_path)
                evidence_label.setText(fname)
                evidence_label.setStyleSheet(f"color: {PRIMARY}; font-size: 12px; font-weight: bold;")

        browse_btn.clicked.connect(browse_evidence)
        evidence_row.addWidget(evidence_label, 1)
        evidence_row.addWidget(browse_btn)
        form_layout.addRow("Evidence:", evidence_row)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = self._make_action_btn("fa5s.times", "Cancel", TEXT_SECONDARY)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        submit_btn = self._make_action_btn("fa5s.paper-plane", "Submit Request", PRIMARY)

        def submit_leave():
            start = start_date_edit.date().toPyDate()
            end = end_date_edit.date().toPyDate()
            days = (end - start).days + 1
            reason = reason_edit.toPlainText().strip()

            if days < 1:
                show_warning(dialog, "Invalid Dates", "End date must be on or after start date.")
                return
            if days > employee.get('leave_credits', 0):
                show_warning(dialog, "Insufficient Credits", f"You only have {employee.get('leave_credits', 0)} leave credits available.")
                return
            if not reason:
                show_warning(dialog, "Missing Reason", "Please provide a reason for your leave request.")
                return

            # Copy evidence file
            saved_evidence_path = None
            if evidence_path[0]:
                import shutil
                evidence_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "evidence")
                os.makedirs(evidence_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = os.path.splitext(evidence_path[0])[1]
                dest_filename = f"leave_{self.employee_id}_{timestamp}{ext}"
                dest_path = os.path.join(evidence_dir, dest_filename)
                try:
                    shutil.copy2(evidence_path[0], dest_path)
                    saved_evidence_path = dest_filename
                except Exception:
                    pass

            leave_type = leave_type_combo.currentText()
            if self.dashboard_controller.create_leave_request(self.employee_id, leave_type, start, end, reason, saved_evidence_path):
                show_info(dialog, "Success", f"Leave request submitted!\nType: {leave_type}\nDuration: {start} to {end} ({days} day(s))\nPending admin approval.")
                dialog.accept()
                self.load_my_requests()
            else:
                show_error(dialog, "Error", "Failed to submit leave request.")

        submit_btn.clicked.connect(submit_leave)
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def show_request_overtime_dialog(self):
        from PyQt6.QtWidgets import QTextEdit, QDoubleSpinBox

        employee = self.dashboard_controller.get_employee_by_id(self.employee_id)
        if not employee:
            show_error(self, "Error", "Could not load employee information.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Request Overtime")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(f"background-color: {CARD_BG};")

        layout = QVBoxLayout()

        info_label = QLabel(
            f"<h3>Request Overtime</h3>"
            f"<p><b>Employee:</b> {employee.get('full_name')}<br>"
            f"<b>Department:</b> {employee.get('department')}</p>"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"padding: 12px; background-color: #FEF3C7; border-radius: 8px; border-left: 4px solid {WARNING};")
        layout.addWidget(info_label)

        form_layout = QFormLayout()

        overtime_date_edit = QDateEdit()
        overtime_date_edit.setDate(QDate.currentDate())
        overtime_date_edit.setCalendarPopup(True)
        overtime_date_edit.setMinimumDate(QDate.currentDate())
        form_layout.addRow("Overtime Date:", overtime_date_edit)

        hours_spinbox = QDoubleSpinBox()
        hours_spinbox.setRange(0.5, 8.0)
        hours_spinbox.setSingleStep(0.5)
        hours_spinbox.setValue(2.0)
        hours_spinbox.setSuffix(" hours")
        form_layout.addRow("Hours Requested:", hours_spinbox)

        from PyQt6.QtWidgets import QTextEdit as QTE2
        reason_edit = QTE2()
        reason_edit.setPlaceholderText("Enter reason for overtime request...")
        reason_edit.setMaximumHeight(100)
        form_layout.addRow("Reason:", reason_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = self._make_action_btn("fa5s.times", "Cancel", TEXT_SECONDARY)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        submit_btn = self._make_action_btn("fa5s.paper-plane", "Submit Request", WARNING)

        def submit_overtime():
            request_date = overtime_date_edit.date().toPyDate()
            hours = hours_spinbox.value()
            reason = reason_edit.toPlainText().strip()

            if not reason:
                show_warning(dialog, "Missing Reason", "Please provide a reason for your overtime request.")
                return
            if self.dashboard_controller.has_pending_overtime(self.employee_id, request_date):
                show_warning(dialog, "Duplicate Request", f"You already have a pending overtime request for {request_date}.")
                return
            existing = self.dashboard_controller.get_approved_overtime_for_date(self.employee_id, request_date)
            if existing:
                show_warning(dialog, "Already Approved", f"You already have approved overtime for {request_date}.")
                return

            if self.dashboard_controller.create_overtime_request(self.employee_id, request_date, hours, reason):
                show_info(dialog, "Success", f"Overtime request submitted!\nDate: {request_date}\nHours: {hours}\nPending admin approval.")
                dialog.accept()
                self.load_my_requests()
            else:
                show_error(dialog, "Error", "Failed to submit overtime request.")

        submit_btn.clicked.connect(submit_overtime)
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()

    # ===== REPORTS =====

    def get_report_data(self):
        """Get report data based on selected type and date range"""
        report_type = self.report_type.currentText()
        start_date = self.report_start_date.date().toPyDate()
        end_date = self.report_end_date.date().toPyDate()

        if report_type == "My Attendance Report":
            report = self.reports_controller.generate_employee_report(
                self.employee_id, start_date, end_date)
            data = report.get('attendance', []) if report else []
            filename = f"my_attendance_{start_date}_to_{end_date}.pdf"
        elif report_type == "My Late Report":
            all_late = self.dashboard_controller.get_employee_late_records(self.employee_id) or []
            data = [r for r in all_late
                    if r.get('date') and start_date <= r['date'] <= end_date]
            filename = f"my_late_report_{start_date}_to_{end_date}.pdf"
        elif report_type == "My Requests Summary":
            leaves = self.dashboard_controller.get_employee_leaves(self.employee_id) or []
            ot = self.dashboard_controller.get_employee_overtime_requests(self.employee_id) or []
            late_cons = self.dashboard_controller.get_employee_late_considerations(self.employee_id) or []

            data = []
            for r in leaves:
                data.append({
                    'Type': 'Leave',
                    'Details': f"{r.get('leave_type', '-')}: {r.get('start_date', '-')} to {r.get('end_date', '-')}",
                    'Status': r.get('status', '-'),
                    'Reason': r.get('reason', '-'),
                    'Requested': str(r.get('requested_at', '-')),
                    'Remarks': r.get('remarks', '') or '-'
                })
            for r in ot:
                data.append({
                    'Type': 'Overtime',
                    'Details': f"{r.get('request_date', '-')} ({r.get('hours_requested', '-')} hrs)",
                    'Status': r.get('status', '-'),
                    'Reason': r.get('reason', '-'),
                    'Requested': str(r.get('created_at', '-')),
                    'Remarks': r.get('remarks', '') or '-'
                })
            for r in late_cons:
                data.append({
                    'Type': 'Late Consideration',
                    'Details': str(r.get('attendance_date', '-')),
                    'Status': r.get('status', '-'),
                    'Reason': r.get('reason', '-'),
                    'Requested': str(r.get('created_at', '-')),
                    'Remarks': r.get('remarks', '') or '-'
                })
            filename = f"my_requests_summary_{start_date}_to_{end_date}.pdf"
        else:
            data = None
            filename = "report.pdf"

        return data, filename

    def export_to_pdf(self):
        data, filename = self.get_report_data()
        if not data:
            show_warning(self, "No Data", "No data to export for the selected criteria.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", filename, "PDF Files (*.pdf)")
        if not file_path:
            return
        success, message = self.reports_controller.export_to_pdf(data, file_path)
        if success:
            show_info(self, "Export Successful", message)
        else:
            show_error(self, "Export Failed", message)
