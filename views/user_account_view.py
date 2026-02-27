"""
User Account Management View
Dialog for creating and managing user login accounts
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from controllers.employee_controller import EmployeeController
from utils.message_box import show_info, show_warning, show_error


class PasswordInputWithToggle(QWidget):
    """Password input field with visibility toggle button"""
    
    def __init__(self, placeholder="Enter password"):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Password input
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        self.input.setStyleSheet("""
            QLineEdit {
                padding: 8px 35px 8px 8px;
                font-size: 14px;
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #5A8AC4;
            }
        """)
        
        # Toggle button
        self.toggle_btn = QPushButton("👁")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 13px;
                color: #687280;
            }
            QPushButton:hover {
                color: #5A8AC4;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_visibility)
        self.is_visible = False
        
        layout.addWidget(self.input)
        
        # Position toggle button inside input
        self.toggle_btn.setParent(self.input)
        self.toggle_btn.move(self.input.width() - 35, 4)
        
        self.setLayout(layout)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.toggle_btn.move(self.input.width() - 35, 4)
    
    def toggle_visibility(self):
        """Toggle password visibility"""
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setText("👁")
    
    def text(self):
        return self.input.text()
    
    def clear(self):
        self.input.clear()
    
    def setFocus(self):
        self.input.setFocus()


class CreateUserAccountDialog(QDialog):
    """Dialog for creating a user login account for an employee"""
    
    def __init__(self, parent=None):
        """Initialize create user account dialog"""
        super().__init__(parent)
        self.employee_controller = EmployeeController()
        self.init_ui()
        self.load_employees()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Create User Account")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Create User Login Account")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333440;")
        layout.addWidget(title)
        
        # Info
        info = QLabel("Create a login account for an employee to access the system.")
        info.setStyleSheet("color: #687280; font-size: 13px; margin-bottom: 10px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Select Employee
        self.employee_combo = QComboBox()
        self.employee_combo.currentIndexChanged.connect(self.on_employee_selected)
        form_layout.addRow("Select Employee*:", self.employee_combo)
        
        # Employee Info Display
        self.employee_info_label = QLabel()
        self.employee_info_label.setStyleSheet("""
            padding: 10px;
            background-color: #E8F4F8;
            border-left: 4px solid #5A8AC4;
            border-radius: 5px;
            color: #333440;
        """)
        self.employee_info_label.setWordWrap(True)
        self.employee_info_label.hide()
        layout.addWidget(self.employee_info_label)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g., john.doe")
        form_layout.addRow("Username*:", self.username_input)
        
        # Password with toggle
        self.password_widget = PasswordInputWithToggle("Enter password")
        form_layout.addRow("Password*:", self.password_widget)
        
        # Confirm Password with toggle
        self.confirm_password_widget = PasswordInputWithToggle("Re-enter password")
        form_layout.addRow("Confirm Password*:", self.confirm_password_widget)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Employee", "Admin"])
        form_layout.addRow("Role*:", self.role_combo)
        
        layout.addLayout(form_layout)
        
        # Required fields note
        note = QLabel("* Required fields")
        note.setStyleSheet("color: #687280; font-size: 12px;")
        layout.addWidget(note)
        
        # Password hint
        hint = QLabel("💡 Tip: Use a strong password with at least 8 characters")
        hint.setStyleSheet("color: #5A8AC4; font-size: 12px; margin-top: 5px;")
        layout.addWidget(hint)
        
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
        
        create_btn = QPushButton("Create Account")
        create_btn.setStyleSheet("""
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
        create_btn.clicked.connect(self.create_account)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #5A8AC4;
            }
        """)
    
    def load_employees(self):
        """Load employees who don't have user accounts yet"""
        all_employees = self.employee_controller.get_all_employees()
        
        # Filter out employees who already have user accounts
        self.available_employees = []
        for emp in all_employees:
            existing_user = self.employee_controller.get_user_by_employee_id(emp['id'])
            if not existing_user and emp['status'] == 'Active':
                self.available_employees.append(emp)
        
        # Populate combo box
        self.employee_combo.clear()
        self.employee_combo.addItem("-- Select an Employee --", None)
        
        for emp in self.available_employees:
            display_text = f"{emp['full_name']} ({emp['department']})"
            self.employee_combo.addItem(display_text, emp)
    
    def on_employee_selected(self, index):
        """Handle employee selection"""
        employee = self.employee_combo.currentData()
        
        if employee:
            # Show employee info
            info_text = f"📋 {employee['full_name']}\n"
            info_text += f"🏢 {employee['position']} - {employee['department']}\n"
            info_text += f"📧 {employee.get('email', 'N/A')}"
            self.employee_info_label.setText(info_text)
            self.employee_info_label.show()
            
            # Suggest username based on name
            name_parts = employee['full_name'].lower().split()
            if len(name_parts) >= 2:
                suggested_username = f"{name_parts[0]}.{name_parts[-1]}"
            else:
                suggested_username = name_parts[0]
            
            self.username_input.setText(suggested_username)
        else:
            self.employee_info_label.hide()
            self.username_input.clear()
    
    def create_account(self):
        """Create user account"""
        # Get selected employee
        employee = self.employee_combo.currentData()
        
        if not employee:
            show_warning(self, "Validation Error", "Please select an employee.")
            return
        
        # Get input values
        username = self.username_input.text().strip().replace(" ", "")
        password = self.password_widget.text()
        confirm_password = self.confirm_password_widget.text()
        role = self.role_combo.currentText()
        
        # Validate inputs
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
            show_warning(self, "Password Mismatch", "Passwords do not match. Please try again.")
            return
        
        # Create user account
        user_id = self.employee_controller.create_user(
            employee['id'],
            username,
            password,
            role
        )
        
        if user_id:
            show_info(
                self,
                "Success",
                f"User account created successfully!\n\n"
                f"Username: {username}\n"
                f"Role: {role}\n\n"
                f"The employee can now login with these credentials."
            )
            self.accept()
        else:
            show_error(
                self,
                "Error",
                "Failed to create user account.\n"
                "The username might already exist."
            )


class ChangePasswordDialog(QDialog):
    """Dialog for users to change their own password"""
    
    def __init__(self, user_data, parent=None):
        """
        Initialize change password dialog
        
        Args:
            user_data: Current logged-in user information
            parent: Parent widget
        """
        super().__init__(parent)
        self.user_data = user_data
        self.user_id = user_data['id']
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Change Password")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("🔐 Change Your Password")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333440;")
        layout.addWidget(title)
        
        # Info
        info = QLabel(f"Changing password for: {self.user_data.get('full_name', 'User')}")
        info.setStyleSheet("color: #687280; font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Current Password
        self.current_password_widget = PasswordInputWithToggle("Enter current password")
        form_layout.addRow("Current Password*:", self.current_password_widget)
        
        # New Password
        self.new_password_widget = PasswordInputWithToggle("Enter new password")
        form_layout.addRow("New Password*:", self.new_password_widget)
        
        # Confirm New Password
        self.confirm_password_widget = PasswordInputWithToggle("Confirm new password")
        form_layout.addRow("Confirm Password*:", self.confirm_password_widget)
        
        layout.addLayout(form_layout)
        
        # Password requirements hint
        hint = QLabel("💡 Password must be at least 8 characters long")
        hint.setStyleSheet("color: #5A8AC4; font-size: 12px; margin-top: 5px;")
        layout.addWidget(hint)
        
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
        
        change_btn = QPushButton("Change Password")
        change_btn.setStyleSheet("""
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
        change_btn.clicked.connect(self.change_password)
        button_layout.addWidget(change_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
        """)
    
    def change_password(self):
        """Handle password change"""
        current_password = self.current_password_widget.text()
        new_password = self.new_password_widget.text()
        confirm_password = self.confirm_password_widget.text()
        
        # Validation
        if not current_password:
            show_warning(self, "Validation Error", "Please enter your current password.")
            return
        
        if not new_password:
            show_warning(self, "Validation Error", "Please enter a new password.")
            return
        
        if len(new_password) < 8:
            show_warning(self, "Weak Password", "Password must be at least 8 characters long.")
            return
        
        if new_password != confirm_password:
            show_warning(self, "Password Mismatch", "New passwords do not match. Please try again.")
            return
        
        if current_password == new_password:
            show_warning(self, "Same Password", "New password must be different from current password.")
            return
        
        # Verify and change password via controller
        employee_controller = EmployeeController()
        success, message = employee_controller.change_password(
            self.user_id, current_password, new_password
        )
        
        if not success and "incorrect" in message.lower():
            show_error(self, "Authentication Failed", "Current password is incorrect.")
            return
        
        if success:
            show_info(
                self,
                "Success",
                "Your password has been changed successfully!\n\n"
                "Please use your new password next time you login."
            )
            self.accept()
        else:
            show_error(self, "Error", "Failed to change password. Please try again.")
