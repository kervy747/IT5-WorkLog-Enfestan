"""
Login Controller (MVC)
Handles login authentication  all DB operations via Database singleton.
Zero UI imports. Returns result tuples for the view to display.
"""

from models.database import db
from models.user_model import UserModel


class LoginController:
    """Controller for login functionality  pure transaction, zero UI"""

    def __init__(self):
        self.db = db
        self.current_user = None

    def authenticate(self, username, password):
        """
        Authenticate user  DB query via model SQL constant.
        Returns (user_or_None, title, message, msg_type)
        """
        if not username or not password:
            return (None, "Validation Error",
                    "Please enter both username and password.", "warning")

        password_hash = UserModel.hash_password(password)
        user = self.db.fetch_one(UserModel.Q_AUTHENTICATE, (username, password_hash))

        if user:
            self.current_user = user
            return (user, "Login Successful",
                    f"Welcome, {user['full_name']}!", "info")
        return (None, "Login Failed",
                "Invalid username or password.\nPlease try again.", "warning")

    def get_current_user(self):
        return self.current_user
