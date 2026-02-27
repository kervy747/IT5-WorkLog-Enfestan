"""
User Model — Pure Blueprint (MVC)
Contains ONLY: TABLE name, FIELDS list, SQL query constants, and pure utility methods.
Zero database imports. Zero query execution.
"""

import hashlib


class UserModel:
    """Data structure and SQL query holder for user accounts"""

    TABLE = 'users'

    FIELDS = [
        'id', 'employee_id', 'username', 'password_hash',
        'role', 'is_active', 'created_at', 'updated_at'
    ]

    # ── SQL Query Constants ──
    Q_INSERT = """
        INSERT INTO users (employee_id, username, password_hash, role, is_active)
        VALUES (%s, %s, %s, %s, 1)
    """

    Q_AUTHENTICATE = """
        SELECT u.*, e.full_name, e.employee_code, e.position, e.department
        FROM users u
        INNER JOIN employees e ON u.employee_id = e.id
        WHERE u.username = %s AND u.password_hash = %s AND u.is_active = 1
    """

    Q_SELECT_BY_ID = "SELECT * FROM users WHERE id = %s"

    Q_SELECT_BY_USERNAME = "SELECT * FROM users WHERE username = %s"

    Q_SELECT_BY_EMPLOYEE_ID = "SELECT * FROM users WHERE employee_id = %s"

    Q_UPDATE_PASSWORD = "UPDATE users SET password_hash = %s WHERE id = %s"

    Q_DEACTIVATE = "UPDATE users SET is_active = 0 WHERE id = %s"

    Q_ACTIVATE = "UPDATE users SET is_active = 1 WHERE id = %s"

    # ── Pure Utility (no DB access) ──
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256 (pure computation, no DB)"""
        return hashlib.sha256(password.encode()).hexdigest()
