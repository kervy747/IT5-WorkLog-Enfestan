"""
User Controller (MVC)
Handles all user account business logic and database operations.
"""

from models.database import db
from models.user_model import UserModel


class UserController:
    """Controller for user account operations"""

    def __init__(self):
        self.db = db

    # ── CRUD Operations ──
    def create_user(self, employee_id, username, password, role):
        """Create a new user account"""
        password_hash = UserModel.hash_password(password)
        params = (employee_id, username, password_hash, role)
        if self.db.execute_query(UserModel.Q_INSERT, params):
            return self.db.get_last_insert_id()
        return None

    def authenticate(self, username, password):
        """
        Authenticate a user by username and password.
        Returns user record (with employee info) or None.
        """
        password_hash = UserModel.hash_password(password)
        return self.db.fetch_one(UserModel.Q_AUTHENTICATE,
                                 (username, password_hash))

    def get_user_by_id(self, user_id):
        """Get user record by ID"""
        return self.db.fetch_one(UserModel.Q_SELECT_BY_ID, (user_id,))

    def get_user_by_username(self, username):
        """Get user record by username"""
        return self.db.fetch_one(UserModel.Q_SELECT_BY_USERNAME, (username,))

    def get_user_by_employee_id(self, employee_id):
        """Get user record by employee ID"""
        return self.db.fetch_one(UserModel.Q_SELECT_BY_EMPLOYEE_ID, (employee_id,))

    # ── Password & Account Management ──
    def change_password(self, user_id, old_password, new_password):
        """
        Change user password after verifying old password.
        Returns (success, message) tuple.
        """
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
        """Update password directly (admin reset)"""
        new_hash = UserModel.hash_password(new_password)
        return self.db.execute_query(UserModel.Q_UPDATE_PASSWORD,
                                     (new_hash, user_id))

    def deactivate_user(self, user_id):
        """Deactivate a user account"""
        return self.db.execute_query(UserModel.Q_DEACTIVATE, (user_id,))

    def activate_user(self, user_id):
        """Activate a user account"""
        return self.db.execute_query(UserModel.Q_ACTIVATE, (user_id,))
