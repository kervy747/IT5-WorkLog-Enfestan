"""
Late Consideration Model — Pure Blueprint (MVC)
Contains ONLY: TABLE name, FIELDS list, SQL query constants, __init__ constructor.
Zero database imports. Zero query execution.
"""


class LateConsiderationModel:
    """Data structure and SQL query holder for late consideration requests"""

    TABLE = 'late_considerations'

    FIELDS = [
        'id', 'employee_id', 'attendance_date', 'reason', 'evidence_path',
        'status', 'reviewed_by', 'reviewed_at', 'remarks',
        'employee_notified', 'created_at', 'updated_at'
    ]

    # ── SQL Query Constants ──
    Q_INSERT = """
        INSERT INTO late_considerations
        (employee_id, attendance_date, reason, evidence_path, status)
        VALUES (%s, %s, %s, %s, 'Pending')
    """

    Q_SELECT_PENDING = """
        SELECT lc.*, e.employee_code, e.full_name, e.department
        FROM late_considerations lc
        INNER JOIN employees e ON lc.employee_id = e.id
        WHERE lc.status = 'Pending'
        ORDER BY lc.created_at ASC
    """

    Q_SELECT_ALL = """
        SELECT lc.*, e.employee_code, e.full_name, e.department,
               r.full_name as reviewer_name
        FROM late_considerations lc
        INNER JOIN employees e ON lc.employee_id = e.id
        LEFT JOIN employees r ON lc.reviewed_by = r.id
        ORDER BY lc.created_at DESC
    """

    Q_SELECT_BY_EMPLOYEE = """
        SELECT lc.*, r.full_name as reviewer_name
        FROM late_considerations lc
        LEFT JOIN employees r ON lc.reviewed_by = r.id
        WHERE lc.employee_id = %s
        ORDER BY lc.created_at DESC
    """

    Q_SELECT_BY_ID = """
        SELECT lc.*, e.full_name, e.employee_code, e.department
        FROM late_considerations lc
        INNER JOIN employees e ON lc.employee_id = e.id
        WHERE lc.id = %s
    """

    Q_APPROVE = """
        UPDATE late_considerations
        SET status = 'Approved', reviewed_by = %s, reviewed_at = %s, remarks = %s
        WHERE id = %s AND status = 'Pending'
    """

    Q_REJECT = """
        UPDATE late_considerations
        SET status = 'Rejected', reviewed_by = %s, reviewed_at = %s, remarks = %s
        WHERE id = %s AND status = 'Pending'
    """

    Q_COUNT_PENDING = "SELECT COUNT(*) as count FROM late_considerations WHERE status = 'Pending'"

    Q_HAS_PENDING = """
        SELECT COUNT(*) as count FROM late_considerations
        WHERE employee_id = %s AND attendance_date = %s AND status = 'Pending'
    """

    Q_SELECT_UNNOTIFIED = """
        SELECT * FROM late_considerations
        WHERE employee_id = %s
          AND status IN ('Approved', 'Rejected')
          AND employee_notified = 0
        ORDER BY reviewed_at DESC
    """

    Q_MARK_ALL_NOTIFIED = """
        UPDATE late_considerations
        SET employee_notified = 1
        WHERE employee_id = %s
          AND status IN ('Approved', 'Rejected')
          AND employee_notified = 0
    """

