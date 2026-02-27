"""
Overtime Model — Pure Blueprint (MVC)
Contains ONLY: TABLE name, FIELDS list, SQL query constants, __init__ constructor.
Zero database imports. Zero query execution.
"""


class OvertimeModel:
    """Data structure and SQL query holder for overtime requests"""

    TABLE = 'overtime_requests'

    FIELDS = [
        'id', 'employee_id', 'request_date', 'hours_requested', 'reason',
        'status', 'reviewed_by', 'reviewed_at', 'remarks', 'actual_overtime',
        'employee_notified', 'created_at', 'updated_at'
    ]

    # ── SQL Query Constants ──
    Q_INSERT = """
        INSERT INTO overtime_requests
        (employee_id, request_date, hours_requested, reason, status)
        VALUES (%s, %s, %s, %s, 'Pending')
    """

    Q_SELECT_PENDING = """
        SELECT o.*, e.full_name, e.employee_code, e.department
        FROM overtime_requests o
        INNER JOIN employees e ON o.employee_id = e.id
        WHERE o.status = 'Pending'
        ORDER BY o.request_date ASC, o.created_at ASC
    """

    Q_SELECT_ALL = """
        SELECT o.*, e.full_name, e.employee_code, e.department,
               r.full_name as reviewer_name
        FROM overtime_requests o
        INNER JOIN employees e ON o.employee_id = e.id
        LEFT JOIN employees r ON o.reviewed_by = r.id
        ORDER BY o.created_at DESC
    """

    Q_SELECT_BY_EMPLOYEE = """
        SELECT o.*, r.full_name as reviewer_name
        FROM overtime_requests o
        LEFT JOIN employees r ON o.reviewed_by = r.id
        WHERE o.employee_id = %s
        ORDER BY o.created_at DESC
    """

    Q_SELECT_BY_ID = """
        SELECT o.*, e.full_name, e.employee_code, e.department
        FROM overtime_requests o
        INNER JOIN employees e ON o.employee_id = e.id
        WHERE o.id = %s
    """

    Q_APPROVE = """
        UPDATE overtime_requests
        SET status = 'Approved', reviewed_by = %s, reviewed_at = %s, remarks = %s
        WHERE id = %s AND status = 'Pending'
    """

    Q_REJECT = """
        UPDATE overtime_requests
        SET status = 'Rejected', reviewed_by = %s, reviewed_at = %s, remarks = %s
        WHERE id = %s AND status = 'Pending'
    """

    Q_SELECT_APPROVED_FOR_DATE = """
        SELECT * FROM overtime_requests
        WHERE employee_id = %s AND request_date = %s AND status = 'Approved'
    """

    Q_UPDATE_ACTUAL = "UPDATE overtime_requests SET actual_overtime = %s WHERE id = %s"

    Q_COUNT_PENDING = "SELECT COUNT(*) as count FROM overtime_requests WHERE status = 'Pending'"

    Q_HAS_PENDING = """
        SELECT COUNT(*) as count FROM overtime_requests
        WHERE employee_id = %s AND request_date = %s AND status = 'Pending'
    """

    Q_MONTHLY_OVERTIME = """
        SELECT COALESCE(SUM(actual_overtime), 0) as total_overtime
        FROM overtime_requests
        WHERE employee_id = %s
          AND status = 'Approved'
          AND YEAR(request_date) = %s
          AND MONTH(request_date) = %s
    """

    Q_SELECT_UNNOTIFIED = """
        SELECT * FROM overtime_requests
        WHERE employee_id = %s
          AND status IN ('Approved', 'Rejected')
          AND employee_notified = 0
        ORDER BY reviewed_at DESC
    """

    Q_MARK_NOTIFIED = "UPDATE overtime_requests SET employee_notified = 1 WHERE id = %s"

    Q_MARK_ALL_NOTIFIED = """
        UPDATE overtime_requests
        SET employee_notified = 1
        WHERE employee_id = %s AND status IN ('Approved', 'Rejected') AND employee_notified = 0
    """
