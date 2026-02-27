"""
Employee Management View
Dialog for adding and editing employees
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QSpinBox, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
from controllers.employee_controller import EmployeeController
from views.user_account_view import PasswordInputWithToggle
from utils.message_box import show_info, show_warning, show_error

# Predefined positions
POSITIONS = [
    "Staff",
    "Software Developer",
    "Software Engineer",
    "Web Developer",
    "App Developer",
    "System Administrator",
    "Database Administrator",
    "Network Engineer",
    "IT Support Specialist",
    "Project Manager",
    "QA Engineer",
    "UI/UX Designer",
    "Data Analyst",
    "DevOps Engineer",
    "Security Analyst",
    "Technical Lead",
    "Team Lead",
    "HR Manager",
    "HR Assistant",
    "Accountant",
    "Marketing Specialist",
    "Sales Representative",
    "Office Administrator",
    "Customer Support",
    "Operations Manager",
]


class AddEmployeeDialog(QDialog):
    """Dialog for adding a new employee and creating user account"""
    
    def __init__(self, parent=None):
        """Initialize add employee dialog"""
        super().__init__(parent)
        self.employee_controller = EmployeeController()
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Add New Employee")
        self.setModal(True)
        self.setMinimumWidth(520)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Add New Employee")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333440;")
        layout.addWidget(title)
        
        info = QLabel("This will create the employee record and a login account.")
        info.setStyleSheet("color: #687280; font-size: 12px; margin-bottom: 5px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # --- Employee Info Section ---
        emp_section = QLabel("Employee Information")
        emp_section.setStyleSheet("font-size: 14px; font-weight: 600; color: #333440; margin-top: 5px;")
        layout.addWidget(emp_section)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Full Name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("e.g., John Smith")
        form_layout.addRow("Full Name*:", self.full_name_input)
        
        # Position (Dropdown)
        self.position_input = QComboBox()
        self.position_input.setEditable(True)
        self.position_input.addItems(POSITIONS)
        self.position_input.setCurrentText("")
        self.position_input.lineEdit().setPlaceholderText("Select or type a position")
        form_layout.addRow("Position*:", self.position_input)
        
        # Department
        self.department_input = QLineEdit()
        self.department_input.setPlaceholderText("e.g., IT")
        form_layout.addRow("Department*:", self.department_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g., john.smith@company.com")
        form_layout.addRow("Email*:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g., +63 917 123 4567")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Leave Credits
        self.leave_credits_input = QSpinBox()
        self.leave_credits_input.setMinimum(0)
        self.leave_credits_input.setMaximum(999)
        self.leave_credits_input.setValue(15)
        form_layout.addRow("Leave Credits:", self.leave_credits_input)
        
        # Shift Assignment
        self.shift_combo = QComboBox()
        self.load_shifts()
        form_layout.addRow("Shift:", self.shift_combo)
        
        layout.addLayout(form_layout)
        
        # --- User Account Section ---
        acct_section = QLabel("Login Account")
        acct_section.setStyleSheet("font-size: 14px; font-weight: 600; color: #333440; margin-top: 10px;")
        layout.addWidget(acct_section)
        
        acct_form = QFormLayout()
        acct_form.setSpacing(10)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g., john.smith")
        acct_form.addRow("Username*:", self.username_input)
        
        self.password_input = PasswordInputWithToggle("Minimum 8 characters")
        acct_form.addRow("Password*:", self.password_input)
        
        self.confirm_password_input = PasswordInputWithToggle("Re-enter password")
        acct_form.addRow("Confirm Password*:", self.confirm_password_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Employee", "Admin"])
        acct_form.addRow("Role*:", self.role_combo)
        
        layout.addLayout(acct_form)
        
        # Auto-suggest username when name changes
        self.full_name_input.textChanged.connect(self._suggest_username)
        
        # Required fields note
        note = QLabel("* Required fields")
        note.setStyleSheet("color: #687280; font-size: 12px;")
        layout.addWidget(note)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #687280;
                color: white;
                padding: 10px 30px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #586270;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Employee")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A8AC4;
                color: white;
                padding: 10px 30px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4A7AB4;
            }
        """)
        save_btn.clicked.connect(self.save_employee)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #5A8AC4;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
    
    def _suggest_username(self, name):
        """Auto-suggest username based on full name"""
        name = name.strip()
        if name:
            parts = name.lower().split()
            if len(parts) >= 2:
                suggested = f"{parts[0]}.{parts[-1]}"
            else:
                suggested = parts[0] if parts else ""
            self.username_input.setText(suggested.replace(" ", ""))
    
    def load_shifts(self):
        """Load available shifts into combo box"""
        from controllers.shift_controller import ShiftController
        shift_ctrl = ShiftController()
        shifts = shift_ctrl.get_all_shifts()
        self.shift_combo.clear()
        
        default_idx = 0
        for idx, shift in enumerate(shifts):
            display_text = shift_ctrl.format_shift_display(shift)
            self.shift_combo.addItem(display_text, shift['id'])
            if shift.get('is_default'):
                default_idx = idx
        
        # Select default shift
        self.shift_combo.setCurrentIndex(default_idx)
    
    def save_employee(self):
        """Save the new employee and create user account"""
        # Gather employee data
        position = self.position_input.currentText().strip() if isinstance(self.position_input, QComboBox) else self.position_input.text().strip()
        
        employee_data = {
            'full_name': self.full_name_input.text().strip(),
            'position': position,
            'department': self.department_input.text().strip(),
            'email': self.email_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'leave_credits': self.leave_credits_input.value(),
            'shift_id': self.shift_combo.currentData()
        }
        
        # Validate user account fields
        username = self.username_input.text().strip().replace(" ", "")
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        role = self.role_combo.currentText()
        
        if not username:
            show_warning(self, "Validation Error", "Please enter a username.")
            return
        
        if not password:
            show_warning(self, "Validation Error", "Please enter a password.")
            return
        
        if len(password) < 8:
            show_warning(self, "Weak Password", "Password should be at least 8 characters long.")
            return
        
        if password != confirm_password:
            show_warning(self, "Password Mismatch", "Passwords do not match.")
            return
        
        # Check if username already exists
        existing = self.employee_controller.get_user_by_username(username)
        if existing:
            show_warning(self, "Username Taken", f"The username '{username}' is already in use.")
            return
        
        # Add employee using controller (validates name, email, phone, etc.)
        employee_id, err = self.employee_controller.add_employee(employee_data)
        if err:
            show_warning(self, "Validation Error", err)
            return

        if employee_id:
            # Create user account
            user_id = self.employee_controller.create_user(employee_id, username, password, role)
            if user_id:
                show_info(
                    self,
                    "Success",
                    f"Employee added and account created!\n\n"
                    f"Username: {username}\n"
                    f"Role: {role}\n\n"
                    f"The employee can now login with these credentials."
                )
                self.accept()
            else:
                show_error(self, "Account Error", "Employee was added but failed to create login account.")


class EditEmployeeDialog(QDialog):
    """Dialog for editing an existing employee"""
    
    def __init__(self, employee_data, parent=None):
        """
        Initialize edit employee dialog
        
        Args:
            employee_data: Dictionary containing employee information
            parent: Parent widget
        """
        super().__init__(parent)
        self.employee_data = employee_data
        self.employee_controller = EmployeeController()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Edit Employee")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Edit Employee Information")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333440;")
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Full Name
        self.full_name_input = QLineEdit()
        form_layout.addRow("Full Name*:", self.full_name_input)
        
        # Position (Dropdown)
        self.position_input = QComboBox()
        self.position_input.setEditable(True)
        self.position_input.addItems(POSITIONS)
        form_layout.addRow("Position*:", self.position_input)
        
        # Department
        self.department_input = QLineEdit()
        form_layout.addRow("Department*:", self.department_input)
        
        # Email
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        form_layout.addRow("Phone:", self.phone_input)
        
        # Leave Credits
        self.leave_credits_input = QSpinBox()
        self.leave_credits_input.setMinimum(0)
        self.leave_credits_input.setMaximum(999)
        form_layout.addRow("Leave Credits:", self.leave_credits_input)
        
        # Shift Assignment
        self.shift_combo = QComboBox()
        self.load_shifts()
        form_layout.addRow("Shift:", self.shift_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #687280;
                color: white;
                padding: 10px 30px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #586270;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A8AC4;
                color: white;
                padding: 10px 30px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4A7AB4;
            }
        """)
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #5A8AC4;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
    
    def load_shifts(self):
        """Load available shifts into combo box"""
        from controllers.shift_controller import ShiftController
        shift_ctrl = ShiftController()
        shifts = shift_ctrl.get_all_shifts()
        self.shift_combo.clear()
        
        for shift in shifts:
            display_text = shift_ctrl.format_shift_display(shift)
            self.shift_combo.addItem(display_text, shift['id'])
    
    def load_data(self):
        """Load employee data into form"""
        self.full_name_input.setText(self.employee_data.get('full_name', ''))
        self.position_input.setCurrentText(self.employee_data.get('position', ''))
        self.department_input.setText(self.employee_data.get('department', ''))
        self.email_input.setText(self.employee_data.get('email', ''))
        self.phone_input.setText(self.employee_data.get('phone', ''))
        self.leave_credits_input.setValue(self.employee_data.get('leave_credits', 15))
        
        # Set shift combo to employee's current shift
        current_shift_id = self.employee_data.get('shift_id')
        if current_shift_id:
            for i in range(self.shift_combo.count()):
                if self.shift_combo.itemData(i) == current_shift_id:
                    self.shift_combo.setCurrentIndex(i)
                    break
    
    def save_changes(self):
        """Save employee changes"""
        # Gather updated data
        updated_data = {
            'full_name': self.full_name_input.text().strip(),
            'position': self.position_input.currentText().strip(),
            'department': self.department_input.text().strip(),
            'email': self.email_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'shift_id': self.shift_combo.currentData()
        }
        
        # Update employee info
        success, err = self.employee_controller.update_employee(
            self.employee_data['id'],
            updated_data
        )

        if not success:
            show_warning(self, "Error", err or "Failed to update employee.")
            return

        # Update leave credits separately
        self.employee_controller.update_leave_credits(
            self.employee_data['id'],
            self.leave_credits_input.value()
        )
        show_info(self, "Success", "Employee information updated successfully!")
        self.accept()
