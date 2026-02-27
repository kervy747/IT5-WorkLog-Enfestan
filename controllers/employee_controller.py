"""
Employee Controller (MVC)
Handles all employee management business logic and database operations.
"""

import re
from models.database import db
from models.employee_model import EmployeeModel
from models.user_model import UserModel


class EmployeeController:
    """Controller for employee management"""

    def __init__(self):
        self.db = db

    # ── Validation (pure logic, no DB) ──
    @staticmethod
    def validate_ph_phone(phone):
        if not phone:
            return True
        cleaned = re.sub(r'[\s\-()]+', '', phone)
        return bool(re.match(r'^(09\d{9}|\+?639\d{9})$', cleaned))

    @staticmethod
    def validate_email(email):
        if not email:
            return True
        return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email))

    # ── Read Operations ──
    def get_all_employees(self):
        return self.db.fetch_all(EmployeeModel.Q_SELECT_ALL)

    def get_all_employees_with_shifts(self):
        return self.db.fetch_all(EmployeeModel.Q_SELECT_WITH_SHIFTS)

    def get_employee_by_id(self, employee_id):
        return self.db.fetch_one(EmployeeModel.Q_SELECT_BY_ID, (employee_id,))

    def get_employee_by_code(self, code):
        return self.db.fetch_one(EmployeeModel.Q_SELECT_BY_CODE, (code,))

    def get_active_employees(self):
        return self.db.fetch_all(EmployeeModel.Q_SELECT_ACTIVE)

    def get_non_admin_employees(self):
        return self.db.fetch_all(EmployeeModel.Q_SELECT_NON_ADMIN)

    def get_employee_count(self):
        result = self.db.fetch_one(EmployeeModel.Q_COUNT)
        return result['cnt'] if result else 0

    # ── Code Generation ──
    def generate_employee_code(self):
        result = self.db.fetch_one(EmployeeModel.Q_LAST_CODE)
        if result and result.get('employee_code'):
            last_code = result['employee_code']
            try:
                num = int(last_code.replace('EMP', '')) + 1
            except ValueError:
                num = 1
        else:
            num = 1
        return f"EMP{num:03d}"

    # ── Create ──
    def add_employee(self, employee_data):
        """
        Validate and insert a new employee.
        Returns (employee_id, None) on success, (None, error_message) on failure.
        """
        required_fields = ['full_name', 'position', 'department']
        for field in required_fields:
            if not employee_data.get(field):
                return None, f"Please enter {field.replace('_', ' ').title()}"

        email = employee_data.get('email', '').strip()
        if email and not self.validate_email(email):
            return None, "Please enter a valid email address (e.g., name@example.com)."

        phone = employee_data.get('phone', '').strip()
        if phone and not self.validate_ph_phone(phone):
            return None, ("Please enter a valid Philippine phone number.\n\n"
                          "Accepted formats:\n    09XXXXXXXXX\n    +639XXXXXXXXX\n    639XXXXXXXXX")

        employee_code = self.generate_employee_code()
        params = (
            employee_code,
            employee_data['full_name'],
            employee_data['position'],
            employee_data['department'],
            employee_data.get('email', ''),
            employee_data.get('phone', ''),
            employee_data.get('leave_credits', 15),
            employee_data.get('shift_id')
        )

        if self.db.execute_query(EmployeeModel.Q_INSERT, params):
            return self.db.get_last_insert_id(), None
        return None, "Failed to add employee. Please try again."

    # ── Update ──
    def update_employee(self, employee_id, employee_data):
        """
        Validate and update an employee record.
        Returns (True, None) on success, (False, error_message) on failure.
        """
        required_fields = ['full_name', 'position', 'department']
        for field in required_fields:
            if not employee_data.get(field):
                return False, f"Please enter {field.replace('_', ' ').title()}"

        email = employee_data.get('email', '').strip()
        if email and not self.validate_email(email):
            return False, "Please enter a valid email address (e.g., name@example.com)."

        phone = employee_data.get('phone', '').strip()
        if phone and not self.validate_ph_phone(phone):
            return False, ("Please enter a valid Philippine phone number.\n\n"
                           "Accepted formats:\n    09XXXXXXXXX\n    +639XXXXXXXXX\n    639XXXXXXXXX")

        shift_id = employee_data.get('shift_id')
        if shift_id is not None:
            params = (
                employee_data['full_name'],
                employee_data['position'],
                employee_data['department'],
                employee_data.get('email', ''),
                employee_data.get('phone', ''),
                shift_id,
                employee_id
            )
            success = self.db.execute_query(EmployeeModel.Q_UPDATE_WITH_SHIFT, params)
        else:
            params = (
                employee_data['full_name'],
                employee_data['position'],
                employee_data['department'],
                employee_data.get('email', ''),
                employee_data.get('phone', ''),
                employee_id
            )
            success = self.db.execute_query(EmployeeModel.Q_UPDATE, params)

        if success:
            return True, None
        return False, "Failed to update employee. Please try again."

    # ── Delete / Deactivate ──
    def deactivate_employee(self, employee_id):
        """Deactivate an employee. Returns True/False."""
        return bool(self.db.execute_query(EmployeeModel.Q_DEACTIVATE, (employee_id,)))

    def delete_employee(self, employee_id):
        """Permanently delete employee and all cascade-related records. Returns True/False."""
        try:
            self.db.execute_query(EmployeeModel.Q_CLEAR_OT_REVIEWED, (employee_id,))
            user_row = self.db.fetch_one(EmployeeModel.Q_SELECT_USER_ID, (employee_id,))
            if user_row:
                self.db.execute_query(EmployeeModel.Q_CLEAR_LEAVE_REVIEWED, (user_row['id'],))
            self.db.execute_query(EmployeeModel.Q_DELETE_OT, (employee_id,))
            self.db.execute_query(EmployeeModel.Q_DELETE_LEAVE, (employee_id,))
            self.db.execute_query(EmployeeModel.Q_DELETE_ATTENDANCE, (employee_id,))
            self.db.execute_query(EmployeeModel.Q_DELETE_USER, (employee_id,))
            return bool(self.db.execute_query(EmployeeModel.Q_DELETE, (employee_id,)))
        except Exception as e:
            print(f"Error deleting employee: {e}")
            return False

    # ── Leave Credits ──
    def update_leave_credits(self, employee_id, leave_credits):
        """
        Update leave credits for an employee.
        Returns (True, None) on success, (False, error_message) on failure.
        """
        if leave_credits < 0:
            return False, "Leave credits cannot be negative."
        success = self.db.execute_query(EmployeeModel.Q_UPDATE_LEAVE_CREDITS,
                                        (leave_credits, employee_id))
        if success:
            return True, None
        return False, "Failed to update leave credits. Please try again."

    # ── User Account Operations (delegates to UserModel SQL) ──
    def get_user_by_username(self, username):
        return self.db.fetch_one(UserModel.Q_SELECT_BY_USERNAME, (username,))

    def get_user_by_employee_id(self, employee_id):
        return self.db.fetch_one(UserModel.Q_SELECT_BY_EMPLOYEE_ID, (employee_id,))

    def get_user_by_id(self, user_id):
        return self.db.fetch_one(UserModel.Q_SELECT_BY_ID, (user_id,))

    def create_user(self, employee_id, username, password, role):
        password_hash = UserModel.hash_password(password)
        params = (employee_id, username, password_hash, role)
        if self.db.execute_query(UserModel.Q_INSERT, params):
            return self.db.get_last_insert_id()
        return None

    def change_password(self, user_id, old_password, new_password):
        user = self.db.fetch_one(UserModel.Q_SELECT_BY_ID, (user_id,))
        if not user:
            return False, "User not found."
        old_hash = UserModel.hash_password(old_password)
        if user['password_hash'] != old_hash:
            return False, "Current password is incorrect."
        new_hash = UserModel.hash_password(new_password)
        if self.db.execute_query(UserModel.Q_UPDATE_PASSWORD, (new_hash, user_id)):
            return True, "Password changed successfully."
        return False, "Failed to update password."

    def update_password(self, user_id, new_password):
        new_hash = UserModel.hash_password(new_password)
        return self.db.execute_query(UserModel.Q_UPDATE_PASSWORD, (new_hash, user_id))
