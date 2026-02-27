"""
Shift Model — Pure Blueprint (MVC)
Contains ONLY: TABLE name, FIELDS list, SQL query constants, and __init__ constructor.
Zero database imports. Zero query execution.
"""


class ShiftModel:
    """Data structure and SQL query holder for work shifts"""

    TABLE = 'shifts'

    FIELDS = [
        'id', 'shift_name', 'start_time', 'end_time', 'work_hours',
        'grace_period_mins', 'min_hours_before_lunch', 'is_default', 'is_active'
    ]

    # ── SQL Query Constants ──
    Q_SELECT_ALL_ACTIVE = "SELECT * FROM shifts WHERE is_active = 1 ORDER BY is_default DESC, shift_name"

    Q_SELECT_ALL = "SELECT * FROM shifts ORDER BY is_default DESC, shift_name"

    Q_SELECT_BY_ID = "SELECT * FROM shifts WHERE id = %s"

    Q_SELECT_DEFAULT = "SELECT * FROM shifts WHERE is_default = 1 AND is_active = 1 LIMIT 1"

    Q_SELECT_FIRST_ACTIVE = "SELECT * FROM shifts WHERE is_active = 1 LIMIT 1"

    Q_SELECT_EMPLOYEE_SHIFT = """
        SELECT s.* FROM shifts s
        INNER JOIN employees e ON e.shift_id = s.id
        WHERE e.id = %s AND s.is_active = 1
    """

    Q_INSERT = """
        INSERT INTO shifts (shift_name, start_time, end_time, work_hours,
                          grace_period_mins, min_hours_before_lunch, is_default)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    Q_UPDATE = """
        UPDATE shifts SET
            shift_name = %s, start_time = %s, end_time = %s,
            work_hours = %s, grace_period_mins = %s,
            min_hours_before_lunch = %s, is_default = %s
        WHERE id = %s
    """

    Q_UNSET_ALL_DEFAULTS = "UPDATE shifts SET is_default = 0"

    Q_UNSET_DEFAULTS_EXCEPT = "UPDATE shifts SET is_default = 0 WHERE id != %s"

    Q_DEACTIVATE = "UPDATE shifts SET is_active = 0 WHERE id = %s AND is_default = 0"

    Q_COUNT_EMPLOYEES = "SELECT COUNT(*) as count FROM employees WHERE shift_id = %s AND status = 'Active'"

    Q_REASSIGN_EMPLOYEES = "UPDATE employees SET shift_id = %s WHERE shift_id = %s"


