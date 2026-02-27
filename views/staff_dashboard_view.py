"""
Staff Dashboard View - Modern Sidebar Design
PyQt6 staff dashboard with sidebar navigation, analytics, employee management,
leave/overtime management, and reports
"""

import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QMessageBox, QDateEdit, QComboBox, QFormLayout, QStackedWidget,
    QScrollArea, QFrame, QGridLayout, QSizePolicy, QSpacerItem,
    QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate, QSize
from PyQt6.QtGui import QPixmap, QColor, QBrush, QFont
import qtawesome as qta
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from controllers.staff_dashboard_controller import StaffDashboardController
from controllers.reports_controller import ReportsController
from controllers.admin_dashboard_controller import AdminDashboardController
from controllers.employee_controller import EmployeeController
from views.employee_management_view import AddEmployeeDialog, EditEmployeeDialog
from views.user_account_view import ChangePasswordDialog
from utils.message_box import show_info, show_warning, show_error, show_question


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
    "#3B82F6": "#DBEAFE",   # PRIMARY -> blue-100
    "#10B981": "#D1FAE5",   # SUCCESS -> emerald-100
    "#F59E0B": "#FEF3C7",   # WARNING -> amber-100
    "#EF4444": "#FEE2E2",   # DANGER -> red-100
    "#06B6D4": "#CFFAFE",   # INFO -> cyan-100
    "#64748B": "#F1F5F9",   # TEXT_SECONDARY -> slate-100
    "#1E293B": "#E2E8F0",   # TEXT_PRIMARY -> slate-200
    "#94A3B8": "#F1F5F9",   # TEXT_MUTED -> slate-100
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

        # Icon container
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

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            border: none;
            background: transparent;
        """)
        text_layout.addWidget(self.value_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 500;
            color: {TEXT_SECONDARY};
            border: none;
            background: transparent;
        """)
        text_layout.addWidget(title_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        self.setLayout(layout)
        self.setStyleSheet(f"""
            QWidget#statCard {{
                background-color: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)

    def set_value(self, value, color=None):
        display_color = color or TEXT_PRIMARY
        self.value_label.setText(str(value))
        self.value_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {display_color};
            border: none;
            background: transparent;
        """)


class StaffDashboardView(QWidget):
    """Staff dashboard view with modern sidebar"""

    finished = pyqtSignal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.employee_id = user_data['employee_id']

        # Initialize controllers
        self.dashboard_controller = StaffDashboardController(self.employee_id)
        self.admin_controller = AdminDashboardController()
        self.employee_controller = EmployeeController()
        self.reports_controller = ReportsController()

        self.init_ui()
        self.load_data()

        # Setup timer for real-time clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

    def init_ui(self):
        """Initialize the modern sidebar UI"""
        self.setWindowTitle("Work Log - Staff Dashboard")
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

        user_role_label = QLabel("Staff")
        user_role_label.setStyleSheet("""
            font-size: 11px; color: #2563EB;
            background-color: #DBEAFE;
            padding: 2px 10px; border-radius: 10px;
            font-weight: 600;
        """)
        user_role_label.setFixedWidth(55)
        user_layout.addWidget(user_role_label)

        # Shift info
        shift = self.dashboard_controller.get_employee_shift(self.user_data['employee_id'])
        if shift:
            shift_display = self.dashboard_controller.format_shift_display(shift)
            shift_label = QLabel(f"  {shift_display}")
            shift_label.setStyleSheet(f"font-size: 11px; color: {SIDEBAR_TEXT}; margin-top: 4px;")
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
            ("fa5s.tachometer-alt", "Dashboard"),
            ("fa5s.chart-bar", "Analytics"),
            ("fa5s.users", "Employees"),
            ("fa5s.calendar-check", "Leave Requests"),
            ("fa5s.business-time", "Overtime"),
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

        self.page_title = QLabel("Dashboard")
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

        self.pages.addWidget(self._create_dashboard_page())
        self.pages.addWidget(self._create_analytics_page())
        self.pages.addWidget(self._create_employee_page())
        self.pages.addWidget(self._create_leave_page())
        self.pages.addWidget(self._create_overtime_page())
        self.pages.addWidget(self._create_reports_page())

        content_layout.addWidget(self.pages)
        content_area.setLayout(content_layout)
        root_layout.addWidget(content_area)

        self.setLayout(root_layout)

        # Set first nav button active
        self.nav_buttons[0].setChecked(True)
        self.update_clock()

    def _on_nav_clicked(self, clicked_btn):
        for i, btn in enumerate(self.nav_buttons):
            if btn == clicked_btn:
                btn.setChecked(True)
                self.pages.setCurrentIndex(i)
                titles = ["Dashboard", "Analytics", "Employees", "Leave Requests", "Overtime", "Reports"]
                self.page_title.setText(titles[i])
            else:
                btn.setChecked(False)

    # ===== PAGE BUILDERS =====

    def _wrap_in_card(self, object_name):
        return f"""
            QWidget#{object_name} {{
                background-color: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: 12px;
            }}
        """

    def _create_dashboard_page(self):
        """Dashboard page with organization-wide analytics"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Stats Cards Row 1
        stats1 = QGridLayout()
        stats1.setSpacing(16)

        self.total_employees_card = StatCard("fa5s.users", "Total Employees", "0", PRIMARY)
        stats1.addWidget(self.total_employees_card, 0, 0)

        self.attendance_rate_card = StatCard("fa5s.chart-line", "Attendance Rate", "0%", SUCCESS)
        stats1.addWidget(self.attendance_rate_card, 0, 1)

        self.avg_hours_card = StatCard("fa5s.clock", "Avg. Hours/Day", "0.0", WARNING)
        stats1.addWidget(self.avg_hours_card, 0, 2)

        self.ontime_rate_card = StatCard("fa5s.check-circle", "On-Time Rate", "0%", INFO)
        stats1.addWidget(self.ontime_rate_card, 0, 3)

        layout.addLayout(stats1)

        # Stats Cards Row 2
        stats2 = QGridLayout()
        stats2.setSpacing(16)

        self.late_today_card = StatCard("fa5s.exclamation-triangle", "Late Today", "0", WARNING)
        stats2.addWidget(self.late_today_card, 0, 0)

        self.absent_today_card = StatCard("fa5s.user-slash", "Absent Today", "0", DANGER)
        stats2.addWidget(self.absent_today_card, 0, 1)

        self.overtime_card = StatCard("fa5s.business-time", "Overtime Hours", "0.0", INFO)
        stats2.addWidget(self.overtime_card, 0, 2)

        self.pending_leaves_card = StatCard("fa5s.calendar-check", "Pending Leaves", "0", TEXT_SECONDARY)
        stats2.addWidget(self.pending_leaves_card, 0, 3)

        layout.addLayout(stats2)

        # Summary table
        summ_frame = QWidget()
        summ_frame.setObjectName("summFrame")
        summ_frame.setStyleSheet(self._wrap_in_card("summFrame"))
        summ_inner = QVBoxLayout()
        summ_inner.setContentsMargins(20, 20, 20, 20)
        summ_inner.setSpacing(12)

        summ_header = QHBoxLayout()
        summ_header.addStretch()
        refresh_btn = self._make_small_btn("fa5s.sync", "Refresh", PRIMARY)
        refresh_btn.clicked.connect(self.load_data)
        summ_header.addWidget(refresh_btn)
        summ_inner.addLayout(summ_header)

        self.dashboard_attendance_table = self._create_table([
            "Name", "Department", "Time In", "Time Out", "Paid Hours", "Status"
        ])
        summ_inner.addWidget(self.dashboard_attendance_table)
        summ_frame.setLayout(summ_inner)
        layout.addWidget(summ_frame)

        container.setLayout(layout)
        scroll.setWidget(container)

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        page.setLayout(page_layout)
        return page

    def _create_analytics_page(self):
        """Analytics page with charts and graphs"""
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # ===== CHARTS ROW =====
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        # -- Donut chart: Today's attendance distribution --
        donut_frame = QWidget()
        donut_frame.setObjectName("donutFrame")
        donut_frame.setStyleSheet(self._wrap_in_card("donutFrame"))
        donut_frame.setFixedHeight(360)
        donut_inner = QVBoxLayout()
        donut_inner.setContentsMargins(16, 12, 16, 12)
        donut_inner.setSpacing(4)
        donut_title = QLabel("Today's Attendance")
        donut_title.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {TEXT_PRIMARY};")
        donut_inner.addWidget(donut_title)

        self.donut_fig = Figure(figsize=(4, 3), dpi=100)
        self.donut_fig.patch.set_facecolor('#FFFFFF')
        self.donut_canvas = FigureCanvas(self.donut_fig)
        self.donut_canvas.setStyleSheet("background-color: #FFFFFF;")
        donut_inner.addWidget(self.donut_canvas, 1)
        donut_frame.setLayout(donut_inner)
        charts_row.addWidget(donut_frame, 1)

        # -- Bar chart: Weekly attendance trend --
        bar_frame = QWidget()
        bar_frame.setObjectName("barFrame")
        bar_frame.setStyleSheet(self._wrap_in_card("barFrame"))
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

        # Today's All Attendance
        att_frame = QWidget()
        att_frame.setObjectName("analyticsAttFrame")
        att_frame.setStyleSheet(self._wrap_in_card("analyticsAttFrame"))
        att_inner = QVBoxLayout()
        att_inner.setContentsMargins(20, 20, 20, 20)
        att_inner.setSpacing(12)

        att_header = QHBoxLayout()
        att_header.addStretch()

        self.analytics_date_filter = QDateEdit()
        self.analytics_date_filter.setDate(QDate.currentDate())
        self.analytics_date_filter.setCalendarPopup(True)
        self.analytics_date_filter.setStyleSheet(self._date_edit_style())
        self.analytics_date_filter.dateChanged.connect(self.load_analytics_attendance)
        att_header.addWidget(self.analytics_date_filter)

        refresh_btn = self._make_small_btn("fa5s.sync", "Refresh", PRIMARY)
        refresh_btn.clicked.connect(self.load_analytics_data)
        att_header.addWidget(refresh_btn)

        att_inner.addLayout(att_header)

        self.analytics_attendance_table = self._create_table([
            "Name", "Department", "Time In", "Time Out", "Paid Hours", "Status"
        ])
        att_inner.addWidget(self.analytics_attendance_table)

        att_frame.setLayout(att_inner)
        layout.addWidget(att_frame)

        container.setLayout(layout)
        scroll.setWidget(container)

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        page.setLayout(page_layout)
        return page

    def _create_employee_page(self):
        """Employee management page with full CRUD operations"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        emp_frame = QWidget()
        emp_frame.setObjectName("empFrame")
        emp_frame.setStyleSheet(self._wrap_in_card("empFrame"))
        emp_inner = QVBoxLayout()
        emp_inner.setContentsMargins(20, 20, 20, 20)
        emp_inner.setSpacing(12)

        emp_header = QHBoxLayout()
        emp_header.addStretch()

        add_btn = self._make_small_btn("fa5s.user-plus", "Add Employee", SUCCESS)
        add_btn.clicked.connect(self.show_add_employee_dialog)
        emp_header.addWidget(add_btn)

        edit_btn = self._make_small_btn("fa5s.edit", "Edit", WARNING)
        edit_btn.clicked.connect(self.edit_selected_employee)
        emp_header.addWidget(edit_btn)

        del_btn = self._make_small_btn("fa5s.trash", "Delete", DANGER)
        del_btn.clicked.connect(self.delete_selected_employee)
        emp_header.addWidget(del_btn)

        ref_emp = self._make_small_btn("fa5s.sync", "Refresh", PRIMARY)
        ref_emp.clicked.connect(self.load_employee_data)
        emp_header.addWidget(ref_emp)

        emp_inner.addLayout(emp_header)

        self.employee_table = self._create_table([
            "Name", "Position", "Department",
            "Email", "Shift", "Leave Credits", "Status"
        ])
        self.employee_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.employee_table.doubleClicked.connect(self.edit_selected_employee)
        emp_inner.addWidget(self.employee_table)
        emp_frame.setLayout(emp_inner)
        layout.addWidget(emp_frame)
        page.setLayout(layout)
        return page

    def _create_leave_page(self):
        """Leave requests management page with approve/reject"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lv_frame = QWidget()
        lv_frame.setObjectName("lvFrame")
        lv_frame.setStyleSheet(self._wrap_in_card("lvFrame"))
        lv_inner = QVBoxLayout()
        lv_inner.setContentsMargins(20, 20, 20, 20)
        lv_inner.setSpacing(12)

        lv_header = QHBoxLayout()
        lv_header.addStretch()

        lv_header.addWidget(QLabel("Filter:"))
        self.leave_filter = QComboBox()
        self.leave_filter.addItems(["Pending", "All", "Approved", "Rejected"])
        self.leave_filter.setStyleSheet(self._combo_style())
        self.leave_filter.currentTextChanged.connect(self.load_leave_data)
        lv_header.addWidget(self.leave_filter)

        ref_lv = self._make_small_btn("fa5s.sync", "Refresh", PRIMARY)
        ref_lv.clicked.connect(self.load_leave_data)
        lv_header.addWidget(ref_lv)
        lv_inner.addLayout(lv_header)

        self.leave_table = self._create_table([
            "Name", "Leave Type", "Start Date", "End Date",
            "Days", "Reason", "Status", "Requested At"
        ])
        self.leave_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.leave_table.doubleClicked.connect(self.show_leave_details)
        lv_inner.addWidget(self.leave_table)

        lv_actions = QHBoxLayout()
        approve_lv = self._make_action_btn("fa5s.check", "Approve", SUCCESS)
        approve_lv.clicked.connect(self.approve_selected_leave)
        lv_actions.addWidget(approve_lv)
        reject_lv = self._make_action_btn("fa5s.times", "Reject", DANGER)
        reject_lv.clicked.connect(self.reject_selected_leave)
        lv_actions.addWidget(reject_lv)
        lv_actions.addStretch()
        lv_inner.addLayout(lv_actions)

        lv_frame.setLayout(lv_inner)
        layout.addWidget(lv_frame)
        page.setLayout(layout)
        return page

    def _create_overtime_page(self):
        """Overtime requests management page with approve/reject"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        ot_frame = QWidget()
        ot_frame.setObjectName("otFrame")
        ot_frame.setStyleSheet(self._wrap_in_card("otFrame"))
        ot_inner = QVBoxLayout()
        ot_inner.setContentsMargins(20, 20, 20, 20)
        ot_inner.setSpacing(12)

        ot_header = QHBoxLayout()
        ot_header.addStretch()

        ot_header.addWidget(QLabel("Filter:"))
        self.overtime_filter = QComboBox()
        self.overtime_filter.addItems(["Pending", "All", "Approved", "Rejected"])
        self.overtime_filter.setStyleSheet(self._combo_style())
        self.overtime_filter.currentTextChanged.connect(self.load_overtime_data)
        ot_header.addWidget(self.overtime_filter)

        ref_ot = self._make_small_btn("fa5s.sync", "Refresh", PRIMARY)
        ref_ot.clicked.connect(self.load_overtime_data)
        ot_header.addWidget(ref_ot)
        ot_inner.addLayout(ot_header)

        self.overtime_table = self._create_table([
            "Name", "Department", "OT Date",
            "Hours", "Reason", "Status", "Requested At"
        ])
        self.overtime_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.overtime_table.doubleClicked.connect(self.show_overtime_details)
        ot_inner.addWidget(self.overtime_table)

        ot_actions = QHBoxLayout()
        approve_ot = self._make_action_btn("fa5s.check", "Approve", SUCCESS)
        approve_ot.clicked.connect(self.approve_selected_overtime)
        ot_actions.addWidget(approve_ot)
        reject_ot = self._make_action_btn("fa5s.times", "Reject", DANGER)
        reject_ot.clicked.connect(self.reject_selected_overtime)
        ot_actions.addWidget(reject_ot)
        ot_actions.addStretch()
        ot_inner.addLayout(ot_actions)

        ot_frame.setLayout(ot_inner)
        layout.addWidget(ot_frame)
        page.setLayout(layout)
        return page

    def _create_reports_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        reports_frame = QWidget()
        reports_frame.setObjectName("reportsFrame")
        reports_frame.setStyleSheet(self._wrap_in_card("reportsFrame"))
        reports_inner = QVBoxLayout()
        reports_inner.setContentsMargins(20, 20, 20, 20)
        reports_inner.setSpacing(20)

        form = QFormLayout()
        form.setSpacing(12)

        self.report_type = QComboBox()
        self.report_type.addItems(["Daily Report", "Department Report", "Employee Report", "Shift Schedule"])
        self.report_type.setStyleSheet(self._combo_style())
        self.report_type.currentTextChanged.connect(self.on_report_type_changed)
        form.addRow("Report Type:", self.report_type)

        self.report_date = QDateEdit()
        self.report_date.setDate(QDate.currentDate())
        self.report_date.setCalendarPopup(True)
        self.report_date.setStyleSheet(self._date_edit_style())
        form.addRow("Date:", self.report_date)

        reports_inner.addLayout(form)

        export_row = QHBoxLayout()
        export_row.setSpacing(12)

        csv_btn = self._make_action_btn("fa5s.file-csv", "Export CSV", SUCCESS)
        csv_btn.clicked.connect(self.export_to_csv)
        export_row.addWidget(csv_btn)

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

    def _make_small_btn(self, icon_name, text, color):
        btn = QPushButton(f" {text}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(34)
        try:
            btn.setIcon(qta.icon(icon_name, color="white"))
            btn.setIconSize(QSize(14, 14))
        except Exception:
            pass
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
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

    def _date_edit_style(self):
        return f"""
            QDateEdit {{
                background-color: white;
                border: 1px solid {CARD_BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
            QDateEdit:focus {{
                border: 1px solid {PRIMARY};
            }}
        """

    def _combo_style(self):
        return f"""
            QComboBox {{
                background-color: white;
                border: 1px solid {CARD_BORDER};
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                color: {TEXT_PRIMARY};
                min-width: 200px;
            }}
            QComboBox:focus {{
                border: 1px solid {PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {TEXT_SECONDARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 1px solid {CARD_BORDER};
                selection-background-color: {PRIMARY};
                selection-color: white;
            }}
        """

    # ===== DATA LOADING =====

    def update_clock(self):
        now = datetime.now()
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))
        self.clock_label.setText(now.strftime("%I:%M:%S %p"))

    def load_data(self):
        self.load_analytics_data()
        self.load_employee_data()
        self.load_leave_data()
        self.load_overtime_data()

    def load_analytics_data(self):
        all_employees = self.dashboard_controller.get_non_admin_employees()
        total_employees = len(all_employees)

        today_attendance = self.dashboard_controller.get_all_attendance(date.today())

        approved_leaves_today = []
        all_leaves = self.dashboard_controller.get_all_leaves("Approved")
        for leave in all_leaves:
            start_date = leave.get('start_date')
            end_date = leave.get('end_date')
            if start_date and end_date:
                if start_date <= date.today() <= end_date:
                    approved_leaves_today.append(leave.get('employee_id'))

        on_leave_count = len(approved_leaves_today)
        present_count = len(today_attendance)
        late_count = sum(1 for r in today_attendance if r.get('status') and 'Late' in str(r.get('status', '')))
        absent_count = total_employees - present_count - on_leave_count

        expected_to_work = total_employees - on_leave_count
        attendance_rate = (present_count / expected_to_work * 100) if expected_to_work > 0 else 0
        ontime_count = present_count - late_count
        ontime_rate = (ontime_count / expected_to_work * 100) if expected_to_work > 0 else 0

        def get_hours(record):
            paid_hours = record.get('paid_hours')
            if paid_hours is None:
                return 0
            if isinstance(paid_hours, Decimal):
                return float(paid_hours)
            return float(paid_hours) if paid_hours else 0

        total_hours = sum(get_hours(r) for r in today_attendance)
        avg_hours = total_hours / present_count if present_count > 0 else 0
        overtime_hours = sum(max(0, get_hours(r) - 8) for r in today_attendance)

        pending_leaves = len(self.dashboard_controller.get_all_leaves("Pending"))

        self.total_employees_card.set_value(str(total_employees), PRIMARY)
        self.attendance_rate_card.set_value(f"{attendance_rate:.1f}%", SUCCESS)
        self.avg_hours_card.set_value(f"{avg_hours:.1f}", WARNING)
        self.ontime_rate_card.set_value(f"{ontime_rate:.1f}%", INFO)
        self.late_today_card.set_value(str(late_count), WARNING)
        self.absent_today_card.set_value(str(absent_count), DANGER)
        self.overtime_card.set_value(f"{overtime_hours:.1f}", INFO)
        self.pending_leaves_card.set_value(str(pending_leaves), TEXT_SECONDARY)

        # ===== UPDATE CHARTS =====
        self._update_donut_chart(present_count - late_count, late_count, absent_count, on_leave_count)
        self._update_bar_chart()

        # ===== UPDATE DASHBOARD TABLE =====
        self.dashboard_attendance_table.setRowCount(len(today_attendance))
        for row, record in enumerate(today_attendance):
            self.dashboard_attendance_table.setItem(row, 0, QTableWidgetItem(str(record.get('full_name', '-'))))
            self.dashboard_attendance_table.setItem(row, 1, QTableWidgetItem(str(record.get('department', '-'))))
            self.dashboard_attendance_table.setItem(row, 2, QTableWidgetItem(self._format_time(record.get('time_in'))))
            self.dashboard_attendance_table.setItem(row, 3, QTableWidgetItem(self._format_time(record.get('time_out'))))
            self.dashboard_attendance_table.setItem(row, 4, QTableWidgetItem(self._format_hours(record.get('paid_hours'))))
            self.dashboard_attendance_table.setItem(row, 5, QTableWidgetItem(str(record.get('status', '-'))))

        self.load_analytics_attendance()

    def load_analytics_attendance(self):
        selected_date = self.analytics_date_filter.date().toPyDate()
        records = self.admin_controller.get_all_attendance(selected_date)

        self.analytics_attendance_table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.analytics_attendance_table.setItem(row, 0, QTableWidgetItem(str(record.get('full_name', '-'))))
            self.analytics_attendance_table.setItem(row, 1, QTableWidgetItem(str(record.get('department', '-'))))
            self.analytics_attendance_table.setItem(row, 2, QTableWidgetItem(self._format_time(record.get('time_in'))))
            self.analytics_attendance_table.setItem(row, 3, QTableWidgetItem(self._format_time(record.get('time_out'))))
            self.analytics_attendance_table.setItem(row, 4, QTableWidgetItem(self._format_hours(record.get('paid_hours'))))
            self.analytics_attendance_table.setItem(row, 5, QTableWidgetItem(str(record.get('status', '-'))))

    # ===== EMPLOYEE MANAGEMENT =====

    def load_employee_data(self):
        employees = self.employee_controller.get_all_employees()
        self.employee_table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            name_item = QTableWidgetItem(str(emp.get('full_name', '-')))
            name_item.setData(Qt.ItemDataRole.UserRole, emp.get('id'))
            self.employee_table.setItem(row, 0, name_item)
            self.employee_table.setItem(row, 1, QTableWidgetItem(str(emp.get('position', '-'))))
            self.employee_table.setItem(row, 2, QTableWidgetItem(str(emp.get('department', '-'))))
            self.employee_table.setItem(row, 3, QTableWidgetItem(str(emp.get('email', '-'))))
            shift_name = '-'
            if emp.get('shift_id'):
                shift = self.dashboard_controller.get_shift_by_id(emp['shift_id'])
                if shift:
                    shift_name = shift.get('shift_name', '-')
            self.employee_table.setItem(row, 4, QTableWidgetItem(shift_name))
            self.employee_table.setItem(row, 5, QTableWidgetItem(str(emp.get('leave_credits', 0))))
            self.employee_table.setItem(row, 6, QTableWidgetItem(str(emp.get('status', '-'))))

    def show_add_employee_dialog(self):
        dialog = AddEmployeeDialog(self)
        if dialog.exec():
            self.load_employee_data()
            self.load_analytics_data()

    def edit_selected_employee(self):
        selected_rows = self.employee_table.selectionModel().selectedRows()
        if not selected_rows:
            show_warning(self, "No Selection", "Please select an employee to edit.")
            return
        row = selected_rows[0].row()
        employee_id = self.employee_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        employee_data = self.dashboard_controller.get_employee_by_id(employee_id)
        if employee_data:
            dialog = EditEmployeeDialog(employee_data, self)
            if dialog.exec():
                self.load_employee_data()

    def delete_selected_employee(self):
        selected_rows = self.employee_table.selectionModel().selectedRows()
        if not selected_rows:
            show_warning(self, "No Selection", "Please select an employee to delete.")
            return
        row = selected_rows[0].row()
        employee_id = self.employee_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        employee_name = self.employee_table.item(row, 0).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Deletion")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(f"background-color: {CARD_BG};")

        layout = QVBoxLayout()
        message = QLabel(
            f"<h3 style='color: #DC2626; margin-bottom: 8px;'>Permanently Delete Employee?</h3>"
            f"<p style='color: {TEXT_PRIMARY};'><b>Name:</b> {employee_name}</p>"
            f"<p style='color: {TEXT_PRIMARY};'><b>WARNING:</b> This will permanently delete:</p>"
            f"<ul style='color: {TEXT_PRIMARY};'><li>Employee record</li><li>User account</li><li>All attendance records</li></ul>"
            f"<p style='color: #DC2626; font-weight: 600;'>This action CANNOT be undone!</p>"
        )
        message.setWordWrap(True)
        message.setStyleSheet(f"""
            padding: 20px;
            background-color: #FEF2F2;
            border-radius: 8px;
            border-left: 4px solid #DC2626;
        """)
        layout.addWidget(message)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = self._make_action_btn("fa5s.times", "Cancel", TEXT_SECONDARY)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        delete_btn = self._make_action_btn("fa5s.trash", "Yes, Delete", DANGER)
        delete_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            if employee_id:
                success = self.employee_controller.delete_employee(employee_id)
                if success:
                    show_info(self, "Deleted", f"{employee_name} has been permanently deleted.")
                    self.load_employee_data()
                    self.load_analytics_data()
                else:
                    show_error(self, "Error", "Failed to delete employee.")

    # ===== LEAVE MANAGEMENT =====

    def load_leave_data(self):
        filter_text = self.leave_filter.currentText()
        if filter_text == "All":
            leaves = self.dashboard_controller.get_all_leaves()
        elif filter_text == "Pending":
            leaves = self.dashboard_controller.get_all_leaves("Pending")
        elif filter_text == "Approved":
            leaves = self.dashboard_controller.get_all_leaves("Approved")
        else:
            leaves = self.dashboard_controller.get_all_leaves("Rejected")

        self.leave_table.setRowCount(len(leaves))
        for row, leave in enumerate(leaves):
            name_item = QTableWidgetItem(str(leave.get('full_name', '-')))
            name_item.setData(Qt.ItemDataRole.UserRole, leave)
            self.leave_table.setItem(row, 0, name_item)
            self.leave_table.setItem(row, 1, QTableWidgetItem(str(leave.get('leave_type', '-'))))
            self.leave_table.setItem(row, 2, QTableWidgetItem(str(leave.get('start_date', '-'))))
            self.leave_table.setItem(row, 3, QTableWidgetItem(str(leave.get('end_date', '-'))))
            self.leave_table.setItem(row, 4, QTableWidgetItem(str(leave.get('days_count', '-'))))
            self.leave_table.setItem(row, 5, QTableWidgetItem(str(leave.get('reason', '-'))))
            status_item = QTableWidgetItem(str(leave.get('status', '-')))
            status = leave.get('status', '')
            if status == 'Approved':
                status_item.setForeground(QBrush(QColor(SUCCESS)))
            elif status == 'Rejected':
                status_item.setForeground(QBrush(QColor(DANGER)))
            elif status == 'Pending':
                status_item.setForeground(QBrush(QColor(WARNING)))
            self.leave_table.setItem(row, 6, status_item)
            self.leave_table.setItem(row, 7, QTableWidgetItem(str(leave.get('requested_at', '-'))))

    def approve_selected_leave(self):
        selected_rows = self.leave_table.selectionModel().selectedRows()
        if not selected_rows:
            show_warning(self, "No Selection", "Please select a leave request to approve.")
            return
        row = selected_rows[0].row()
        leave_data = self.leave_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        leave_id = leave_data.get('id')
        employee_name = self.leave_table.item(row, 0).text()
        days = self.leave_table.item(row, 4).text()
        status = self.leave_table.item(row, 6).text()
        if status != 'Pending':
            show_warning(self, "Invalid Action", f"This leave request has already been {status.lower()}.")
            return
        if show_question(self, "Approve Leave", f"Approve leave request for {employee_name}?\n\nThis will deduct {days} day(s) from their leave credits."):
            admin_user_id = self.user_data.get('id')
            if self.dashboard_controller.approve_leave(leave_id, admin_user_id):
                show_info(self, "Success", f"Leave request approved for {employee_name}.")
                self.load_leave_data()
                self.load_analytics_data()
            else:
                show_error(self, "Error", "Failed to approve leave. Employee may not have enough leave credits.")

    def reject_selected_leave(self):
        selected_rows = self.leave_table.selectionModel().selectedRows()
        if not selected_rows:
            show_warning(self, "No Selection", "Please select a leave request to reject.")
            return
        row = selected_rows[0].row()
        leave_data = self.leave_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        leave_id = leave_data.get('id')
        employee_name = self.leave_table.item(row, 0).text()
        status = self.leave_table.item(row, 6).text()
        if status != 'Pending':
            show_warning(self, "Invalid Action", f"This leave request has already been {status.lower()}.")
            return
        from PyQt6.QtWidgets import QInputDialog
        remarks, ok = QInputDialog.getText(self, "Reject Leave", f"Reject leave request for {employee_name}?\n\nReason (optional):")
        if ok:
            admin_user_id = self.user_data.get('id')
            if self.dashboard_controller.reject_leave(leave_id, admin_user_id, remarks if remarks else None):
                show_info(self, "Success", f"Leave request rejected for {employee_name}.")
                self.load_leave_data()
                self.load_analytics_data()
            else:
                show_error(self, "Error", "Failed to reject leave request.")

    def show_leave_details(self):
        selected_rows = self.leave_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        leave_data = self.leave_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if not leave_data:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Leave Request Details")
        dialog.setModal(True)
        dialog.setMinimumWidth(600)
        dialog.setStyleSheet(f"background-color: {CARD_BG};")

        layout = QVBoxLayout()

        status = leave_data.get('status', 'N/A')
        if status == 'Approved':
            status_color, status_bg = SUCCESS, get_light_bg(SUCCESS)
        elif status == 'Rejected':
            status_color, status_bg = DANGER, get_light_bg(DANGER)
        else:
            status_color, status_bg = WARNING, get_light_bg(WARNING)

        status_label = QLabel(f"<h2 style='color: {status_color};'>Status: {status}</h2>")
        status_label.setStyleSheet(f"padding: 15px; background-color: {status_bg}; border-radius: 8px;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)

        employee_info = QLabel(
            f"<h3>Employee Information</h3>"
            f"<table style='width: 100%;'>"
            f"<tr><td><b>Name:</b></td><td>{leave_data.get('full_name', 'N/A')}</td></tr>"
            f"<tr><td><b>Department:</b></td><td>{leave_data.get('department', 'N/A')}</td></tr>"
            f"<tr><td><b>Leave Credits:</b></td><td>{leave_data.get('leave_credits', 'N/A')} days</td></tr>"
            f"</table>"
        )
        employee_info.setWordWrap(True)
        employee_info.setStyleSheet(f"padding: 15px; background-color: {CONTENT_BG}; border-radius: 8px;")
        layout.addWidget(employee_info)

        leave_info = QLabel(
            f"<h3>Leave Details</h3>"
            f"<table style='width: 100%;'>"
            f"<tr><td><b>Leave Type:</b></td><td>{leave_data.get('leave_type', 'N/A')}</td></tr>"
            f"<tr><td><b>Start Date:</b></td><td>{leave_data.get('start_date', 'N/A')}</td></tr>"
            f"<tr><td><b>End Date:</b></td><td>{leave_data.get('end_date', 'N/A')}</td></tr>"
            f"<tr><td><b>Days:</b></td><td style='font-weight: bold; color: {PRIMARY};'>{leave_data.get('days_count', 'N/A')}</td></tr>"
            f"<tr><td><b>Requested:</b></td><td>{leave_data.get('requested_at', 'N/A')}</td></tr>"
            f"</table>"
        )
        leave_info.setWordWrap(True)
        leave_info.setStyleSheet(f"padding: 15px; background-color: {get_light_bg(PRIMARY)}; border-radius: 8px;")
        layout.addWidget(leave_info)

        reason_label = QLabel("<h3>Reason</h3>")
        layout.addWidget(reason_label)
        reason_text = QLabel(f"<p>{leave_data.get('reason', 'No reason provided.')}</p>")
        reason_text.setWordWrap(True)
        reason_text.setStyleSheet(f"padding: 15px; background-color: {get_light_bg(WARNING)}; border-radius: 8px; border: 1px solid {WARNING};")
        layout.addWidget(reason_text)

        if leave_data.get('reviewed_at'):
            review_info = QLabel(
                f"<h3>Review Information</h3>"
                f"<table style='width: 100%;'>"
                f"<tr><td><b>Reviewed On:</b></td><td>{leave_data.get('reviewed_at', 'N/A')}</td></tr>"
                f"<tr><td><b>Remarks:</b></td><td>{leave_data.get('remarks', 'No remarks')}</td></tr>"
                f"</table>"
            )
            review_info.setWordWrap(True)
            review_info.setStyleSheet(f"padding: 15px; background-color: {CONTENT_BG}; border-radius: 8px;")
            layout.addWidget(review_info)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        pdf_btn = self._make_action_btn("fa5s.file-pdf", "Generate PDF", SUCCESS)
        pdf_btn.clicked.connect(lambda: self._generate_leave_pdf(leave_data))
        button_layout.addWidget(pdf_btn)
        close_btn = self._make_action_btn("fa5s.times", "Close", PRIMARY)
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def _generate_leave_pdf(self, leave_data):
        """Generate PDF for a leave request"""
        from datetime import datetime as dt
        employee_name = leave_data.get('full_name', 'Unknown')
        safe_name = employee_name.replace(' ', '_')
        filename = f"leave_request_{safe_name}_{dt.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Leave Request PDF", filename, "PDF Files (*.pdf)")
        if not file_path:
            return
        reports = ReportsController()
        success, message = reports.generate_leave_request_pdf(leave_data, file_path)
        if success:
            show_info(self, "PDF Generated", message)
        else:
            show_error(self, "PDF Generation Failed", message)

    # ===== OVERTIME MANAGEMENT =====

    def load_overtime_data(self):
        filter_text = self.overtime_filter.currentText()
        if filter_text == "All":
            overtimes = self.dashboard_controller.get_all_overtime_requests()
        elif filter_text == "Pending":
            overtimes = self.dashboard_controller.get_pending_overtime_requests()
        elif filter_text == "Approved":
            all_requests = self.dashboard_controller.get_all_overtime_requests()
            overtimes = [r for r in all_requests if r.get('status') == 'Approved']
        else:
            all_requests = self.dashboard_controller.get_all_overtime_requests()
            overtimes = [r for r in all_requests if r.get('status') == 'Rejected']

        self.overtime_table.setRowCount(len(overtimes))
        for row, ot in enumerate(overtimes):
            name_item = QTableWidgetItem(str(ot.get('full_name', '-')))
            name_item.setData(Qt.ItemDataRole.UserRole, ot)
            self.overtime_table.setItem(row, 0, name_item)
            self.overtime_table.setItem(row, 1, QTableWidgetItem(str(ot.get('department', '-'))))
            self.overtime_table.setItem(row, 2, QTableWidgetItem(str(ot.get('request_date', '-'))))
            self.overtime_table.setItem(row, 3, QTableWidgetItem(f"{ot.get('hours_requested', 0):.1f} hrs"))
            reason = str(ot.get('reason', '-'))
            if len(reason) > 50:
                reason = reason[:47] + "..."
            self.overtime_table.setItem(row, 4, QTableWidgetItem(reason))
            status_item = QTableWidgetItem(str(ot.get('status', '-')))
            status = ot.get('status', '')
            if status == 'Approved':
                status_item.setForeground(QBrush(QColor(SUCCESS)))
            elif status == 'Rejected':
                status_item.setForeground(QBrush(QColor(DANGER)))
            elif status == 'Pending':
                status_item.setForeground(QBrush(QColor(WARNING)))
            self.overtime_table.setItem(row, 5, status_item)
            self.overtime_table.setItem(row, 6, QTableWidgetItem(str(ot.get('created_at', '-'))))

    def approve_selected_overtime(self):
        selected_rows = self.overtime_table.selectionModel().selectedRows()
        if not selected_rows:
            show_warning(self, "No Selection", "Please select an overtime request to approve.")
            return
        row = selected_rows[0].row()
        ot_data = self.overtime_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        ot_id = ot_data.get('id')
        employee_name = self.overtime_table.item(row, 0).text()
        hours = ot_data.get('hours_requested', 0)
        ot_date = ot_data.get('request_date')
        status = self.overtime_table.item(row, 5).text()
        if status != 'Pending':
            show_warning(self, "Invalid Action", f"This overtime request has already been {status.lower()}.")
            return
        if show_question(self, "Approve Overtime", f"Approve overtime request for {employee_name}?\n\nDate: {ot_date}\nHours: {hours}"):
            admin_employee_id = self.user_data.get('employee_id')
            if self.dashboard_controller.approve_overtime(ot_id, admin_employee_id):
                show_info(self, "Success", f"Overtime request approved for {employee_name}.")
                self.load_overtime_data()
                self.load_analytics_data()
            else:
                show_error(self, "Error", "Failed to approve overtime request.")

    def reject_selected_overtime(self):
        selected_rows = self.overtime_table.selectionModel().selectedRows()
        if not selected_rows:
            show_warning(self, "No Selection", "Please select an overtime request to reject.")
            return
        row = selected_rows[0].row()
        ot_data = self.overtime_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        ot_id = ot_data.get('id')
        employee_name = self.overtime_table.item(row, 0).text()
        status = self.overtime_table.item(row, 5).text()
        if status != 'Pending':
            show_warning(self, "Invalid Action", f"This overtime request has already been {status.lower()}.")
            return
        from PyQt6.QtWidgets import QInputDialog
        remarks, ok = QInputDialog.getText(self, "Reject Overtime", f"Reject overtime request for {employee_name}?\n\nReason (optional):")
        if ok:
            admin_employee_id = self.user_data.get('employee_id')
            if self.dashboard_controller.reject_overtime(ot_id, admin_employee_id, remarks if remarks else None):
                show_info(self, "Success", f"Overtime request rejected for {employee_name}.")
                self.load_overtime_data()
                self.load_analytics_data()
            else:
                show_error(self, "Error", "Failed to reject overtime request.")

    def show_overtime_details(self):
        selected_rows = self.overtime_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        ot_data = self.overtime_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if not ot_data:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Overtime Request Details")
        dialog.setModal(True)
        dialog.setMinimumWidth(600)
        dialog.setStyleSheet(f"background-color: {CARD_BG};")

        layout = QVBoxLayout()

        status = ot_data.get('status', 'N/A')
        if status == 'Approved':
            status_color, status_bg = SUCCESS, get_light_bg(SUCCESS)
        elif status == 'Rejected':
            status_color, status_bg = DANGER, get_light_bg(DANGER)
        else:
            status_color, status_bg = WARNING, get_light_bg(WARNING)

        status_label = QLabel(f"<h2 style='color: {status_color};'>Status: {status}</h2>")
        status_label.setStyleSheet(f"padding: 15px; background-color: {status_bg}; border-radius: 8px;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)

        employee_info = QLabel(
            f"<h3>Employee Information</h3>"
            f"<table style='width: 100%;'>"
            f"<tr><td><b>Name:</b></td><td>{ot_data.get('full_name', 'N/A')}</td></tr>"
            f"<tr><td><b>Department:</b></td><td>{ot_data.get('department', 'N/A')}</td></tr>"
            f"</table>"
        )
        employee_info.setWordWrap(True)
        employee_info.setStyleSheet(f"padding: 15px; background-color: {CONTENT_BG}; border-radius: 8px;")
        layout.addWidget(employee_info)

        ot_info = QLabel(
            f"<h3>Overtime Details</h3>"
            f"<table style='width: 100%;'>"
            f"<tr><td><b>Overtime Date:</b></td><td>{ot_data.get('request_date', 'N/A')}</td></tr>"
            f"<tr><td><b>Hours Requested:</b></td><td style='font-weight: bold; color: {WARNING};'>{ot_data.get('hours_requested', 0):.1f} hour(s)</td></tr>"
            f"<tr><td><b>Requested On:</b></td><td>{ot_data.get('created_at', 'N/A')}</td></tr>"
            f"</table>"
        )
        ot_info.setWordWrap(True)
        ot_info.setStyleSheet(f"padding: 15px; background-color: {get_light_bg(WARNING)}; border-radius: 8px;")
        layout.addWidget(ot_info)

        reason_label = QLabel("<h3>Reason</h3>")
        layout.addWidget(reason_label)
        reason_text = QLabel(f"<p>{ot_data.get('reason', 'No reason provided.')}</p>")
        reason_text.setWordWrap(True)
        reason_text.setStyleSheet(f"padding: 15px; background-color: {get_light_bg(WARNING)}; border-radius: 8px; border: 1px solid {WARNING};")
        layout.addWidget(reason_text)

        if ot_data.get('reviewed_at'):
            actual_ot = ot_data.get('actual_overtime')
            actual_text = f"{actual_ot:.1f} hour(s)" if actual_ot else "Not yet recorded"
            review_info = QLabel(
                f"<h3>Review Information</h3>"
                f"<table style='width: 100%;'>"
                f"<tr><td><b>Reviewed On:</b></td><td>{ot_data.get('reviewed_at', 'N/A')}</td></tr>"
                f"<tr><td><b>Reviewed By:</b></td><td>{ot_data.get('reviewer_name', 'N/A')}</td></tr>"
                f"<tr><td><b>Remarks:</b></td><td>{ot_data.get('remarks', 'No remarks')}</td></tr>"
                f"<tr><td><b>Actual OT Worked:</b></td><td>{actual_text}</td></tr>"
                f"</table>"
            )
            review_info.setWordWrap(True)
            review_info.setStyleSheet(f"padding: 15px; background-color: {CONTENT_BG}; border-radius: 8px;")
            layout.addWidget(review_info)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = self._make_action_btn("fa5s.times", "Close", PRIMARY)
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()

    # ===== UTILITY =====

    def _format_time(self, time_value):
        if time_value:
            if hasattr(time_value, 'strftime'):
                return time_value.strftime('%I:%M %p')
            return str(time_value)
        return '-'

    def _format_hours(self, hours_value):
        if hours_value is not None:
            return f"{hours_value:.2f}"
        return '-'

    # ===== CHART HELPERS =====

    def _update_donut_chart(self, on_time, late, absent, on_leave):
        """Render a donut chart showing today's attendance distribution."""
        self.donut_fig.clear()
        ax = self.donut_fig.add_subplot(111)

        values = [on_time, late, absent, on_leave]
        labels = ['On-Time', 'Late', 'Absent', 'On Leave']
        colors = [SUCCESS, WARNING, DANGER, INFO]

        filtered = [(v, l, c) for v, l, c in zip(values, labels, colors) if v > 0]
        if not filtered:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                    fontsize=13, color=TEXT_SECONDARY, transform=ax.transAxes)
            ax.axis('off')
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

        self.donut_fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        self.donut_canvas.draw()

    def _update_bar_chart(self):
        """Render a bar chart showing the last 7 days attendance trend."""
        self.bar_fig.clear()
        ax = self.bar_fig.add_subplot(111)

        summary = self.dashboard_controller.get_weekly_attendance_summary()
        if not summary:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                    fontsize=13, color=TEXT_SECONDARY, transform=ax.transAxes)
            ax.axis('off')
            self.bar_fig.subplots_adjust(left=0.08, right=0.97, top=0.92, bottom=0.12)
            self.bar_canvas.draw()
            return

        dates = [row['date'].strftime('%a\n%m/%d') if hasattr(row['date'], 'strftime')
                 else str(row['date']) for row in summary]
        present_vals = [row['present_count'] - row['late_count'] for row in summary]
        late_vals = [row['late_count'] for row in summary]

        x = range(len(dates))
        bar_width = 0.55

        ax.bar(x, present_vals, bar_width, label='On-Time', color=SUCCESS, edgecolor='white', linewidth=0.5)
        ax.bar(x, late_vals, bar_width, bottom=present_vals, label='Late', color=WARNING, edgecolor='white', linewidth=0.5)

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

        self.bar_fig.subplots_adjust(left=0.08, right=0.97, top=0.92, bottom=0.12)
        self.bar_canvas.draw()
        self.bar_canvas.draw()

    # ===== AUTH =====

    def show_change_password_dialog(self):
        dialog = ChangePasswordDialog(self.user_data, self)
        dialog.exec()

    def handle_logout(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Logout")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet(f"background-color: {CARD_BG};")

        layout = QVBoxLayout()
        message = QLabel("<h3>Confirm Logout</h3><p>Are you sure you want to logout?</p>")
        message.setWordWrap(True)
        message.setStyleSheet("padding: 20px;")
        layout.addWidget(message)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        no_btn = self._make_action_btn("fa5s.times", "Cancel", TEXT_SECONDARY)
        no_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(no_btn)
        yes_btn = self._make_action_btn("fa5s.check", "Yes, Logout", PRIMARY)
        yes_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(yes_btn)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.finished.emit()
            self.close()

    # ===== REPORTS =====

    def on_report_type_changed(self, report_type):
        if report_type == "Shift Schedule":
            self.report_date.setEnabled(False)
        else:
            self.report_date.setEnabled(True)

    def export_to_csv(self):
        data, filename = self.get_report_data()
        if not data:
            show_warning(self, "No Data", "No data to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV Report", filename.replace('.pdf', '.csv'),
            "CSV Files (*.csv)")
        if not file_path:
            return
        success, message = self.reports_controller.export_to_csv(data, file_path)
        if success:
            show_info(self, "Export Successful", message)
        else:
            show_error(self, "Export Failed", message)

    def export_to_pdf(self):
        data, filename = self.get_report_data()
        if not data:
            show_warning(self, "No Data", "No data to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", filename,
            "PDF Files (*.pdf)")
        if not file_path:
            return
        success, message = self.reports_controller.export_to_pdf(data, file_path)
        if success:
            show_info(self, "Export Successful", message)
        else:
            show_error(self, "Export Failed", message)

    def get_report_data(self):
        report_type = self.report_type.currentText()
        target_date = self.report_date.date().toPyDate()

        if report_type == "Daily Report":
            data = self.admin_controller.get_all_attendance(target_date)
            filename = f"daily_report_{target_date}.pdf"
        elif report_type == "Department Report":
            data = self.admin_controller.get_all_attendance(target_date)
            filename = f"department_report_{target_date}.pdf"
        elif report_type == "Employee Report":
            data = self.employee_controller.get_all_employees()
            filename = f"employee_report_{target_date}.pdf"
        elif report_type == "Shift Schedule":
            data = self._get_shift_schedule_data()
            filename = f"shift_schedule_{target_date}.pdf"
        else:
            data = None
            filename = "report.pdf"

        return data, filename

    def _get_shift_schedule_data(self):
        employees = self.dashboard_controller.get_all_employees()
        data = []
        for emp in employees:
            shift = None
            if emp.get('shift_id'):
                shift = self.dashboard_controller.get_shift_by_id(emp['shift_id'])

            data.append({
                'Employee Name': emp.get('full_name', '-'),
                'Department': emp.get('department', '-'),
                'Shift Name': shift.get('shift_name', 'Not Assigned') if shift else 'Not Assigned',
                'Start Time': self._format_shift_time(shift.get('start_time')) if shift else '-',
                'End Time': self._format_shift_time(shift.get('end_time')) if shift else '-',
                'Work Hours': f"{shift.get('work_hours', 8):.1f}" if shift else '-',
                'Grace Period': f"{shift.get('grace_period_mins', 15)} mins" if shift else '-'
            })

        return data

    def _format_shift_time(self, time_val):
        if not time_val:
            return "-"
        if isinstance(time_val, timedelta):
            total_seconds = int(time_val.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            time_str = f"{hours:02d}:{minutes:02d}:00"
        else:
            time_str = str(time_val)
        try:
            time_obj = datetime.strptime(time_str, '%H:%M:%S')
            return time_obj.strftime('%I:%M %p').lstrip('0')
        except:
            return str(time_val)
