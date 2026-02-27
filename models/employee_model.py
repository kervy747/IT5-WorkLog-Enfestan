"""
Employee Model — Pure Blueprint (MVC)
Contains ONLY: TABLE name, FIELDS list, SQL query constants, __init__ constructor.
Zero database imports. Zero query execution.
"""


class EmployeeModel:
    """Data structure and SQL query holder for employees"""

    TABLE = 'employees'

    FIELDS = [
        'id', 'employee_code', 'full_name', 'position', 'department',
        'email', 'phone', 'leave_credits', 'shift_id', 'status',
        'created_at', 'updated_at'
    ]

    # ── SQL Query Constants ──
    Q_SELECT_ALL = "SELECT * FROM employees ORDER BY full_name"

    Q_SELECT_BY_ID = "SELECT * FROM employees WHERE id = %s"

    Q_SELECT_BY_CODE = "SELECT * FROM employees WHERE employee_code = %s"

    Q_SELECT_ACTIVE = "SELECT * FROM employees WHERE status = 'Active' ORDER BY full_name"

    Q_SELECT_NON_ADMIN = """
        SELECT e.* FROM employees e
        LEFT JOIN users u ON e.id = u.employee_id
        WHERE u.role IS NULL OR u.role != 'Admin'
        ORDER BY e.full_name
    """

    Q_INSERT = """
        INSERT INTO employees (employee_code, full_name, position, department,
                               email, phone, leave_credits, shift_id, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Active')
    """

    Q_UPDATE = """
        UPDATE employees
        SET full_name = %s, position = %s, department = %s,
            email = %s, phone = %s
        WHERE id = %s
    """

    Q_UPDATE_WITH_SHIFT = """
        UPDATE employees
        SET full_name = %s, position = %s, department = %s,
            email = %s, phone = %s, shift_id = %s
        WHERE id = %s
    """

    Q_UPDATE_LEAVE_CREDITS = "UPDATE employees SET leave_credits = %s WHERE id = %s"

    Q_DEACTIVATE = "UPDATE employees SET status = 'Inactive' WHERE id = %s"

    Q_ACTIVATE = "UPDATE employees SET status = 'Active' WHERE id = %s"

    Q_DELETE = "DELETE FROM employees WHERE id = %s"

    Q_SELECT_BY_DEPARTMENT = "SELECT * FROM employees WHERE department = %s ORDER BY full_name"

    Q_UPDATE_SHIFT = "UPDATE employees SET shift_id = %s WHERE id = %s"

    Q_SELECT_WITH_SHIFTS = """
        SELECT e.*, s.shift_name, s.start_time as shift_start,
               s.end_time as shift_end, s.grace_period_mins
        FROM employees e
        LEFT JOIN shifts s ON e.shift_id = s.id
        ORDER BY e.full_name
    """

    Q_LAST_CODE = "SELECT employee_code FROM employees WHERE employee_code LIKE 'EMP%%' ORDER BY employee_code DESC LIMIT 1"

    Q_COUNT = "SELECT COUNT(*) as cnt FROM employees"

    # ── Cascade Delete Helper Queries ──
    Q_CLEAR_OT_REVIEWED = "UPDATE overtime_requests SET reviewed_by = NULL WHERE reviewed_by = %s"
    Q_DELETE_OT = "DELETE FROM overtime_requests WHERE employee_id = %s"
    Q_SELECT_USER_ID = "SELECT id FROM users WHERE employee_id = %s"
    Q_CLEAR_LEAVE_REVIEWED = "UPDATE leave_requests SET reviewed_by = NULL WHERE reviewed_by = %s"
    Q_DELETE_LEAVE = "DELETE FROM leave_requests WHERE employee_id = %s"
    Q_DELETE_ATTENDANCE = "DELETE FROM attendance WHERE employee_id = %s"
    Q_DELETE_USER = "DELETE FROM users WHERE employee_id = %s"

