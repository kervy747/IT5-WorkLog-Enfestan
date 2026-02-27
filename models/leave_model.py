"""
Leave Model — Pure Blueprint (MVC)
Contains ONLY: TABLE name, FIELDS list, SQL query constants, __init__ constructor.
Zero database imports. Zero query execution.
"""


class LeaveModel:
    """Data structure and SQL query holder for leave requests"""

    TABLE = 'leave_requests'

    FIELDS = [
        'id', 'employee_id', 'leave_type', 'start_date', 'end_date',
        'days_count', 'reason', 'evidence_path', 'status', 'requested_at',
        'reviewed_by', 'reviewed_at', 'remarks', 'employee_notified'
    ]

    # ── SQL Query Constants ──
    Q_INSERT = """
        INSERT INTO leave_requests
        (employee_id, leave_type, start_date, end_date, days_count, reason, evidence_path, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
    """

    Q_SELECT_PENDING = """
        SELECT lr.*, e.employee_code, e.full_name, e.department, e.leave_credits
        FROM leave_requests lr
        INNER JOIN employees e ON lr.employee_id = e.id
        WHERE lr.status = 'Pending'
        ORDER BY lr.requested_at ASC
    """

    Q_SELECT_ALL = """
        SELECT lr.*, e.employee_code, e.full_name, e.department, e.leave_credits
        FROM leave_requests lr
        INNER JOIN employees e ON lr.employee_id = e.id
        ORDER BY lr.requested_at DESC
    """

    Q_SELECT_BY_STATUS = """
        SELECT lr.*, e.employee_code, e.full_name, e.department, e.leave_credits
        FROM leave_requests lr
        INNER JOIN employees e ON lr.employee_id = e.id
        WHERE lr.status = %s
        ORDER BY lr.requested_at DESC
    """

    Q_SELECT_BY_EMPLOYEE = """
        SELECT * FROM leave_requests
        WHERE employee_id = %s
        ORDER BY requested_at DESC
    """

    Q_SELECT_BY_ID = "SELECT * FROM leave_requests WHERE id = %s"

    Q_APPROVE = """
        UPDATE leave_requests
        SET status = 'Approved', reviewed_by = %s, reviewed_at = NOW(), remarks = %s
        WHERE id = %s
    """

    Q_REJECT = """
        UPDATE leave_requests
        SET status = 'Rejected', reviewed_by = %s, reviewed_at = NOW(), remarks = %s
        WHERE id = %s
    """

    Q_SELECT_EMPLOYEE_CREDITS = "SELECT leave_credits FROM employees WHERE id = %s"

    Q_DEDUCT_CREDITS = "UPDATE employees SET leave_credits = leave_credits - %s WHERE id = %s"

    Q_COUNT_PENDING = "SELECT COUNT(*) as count FROM leave_requests WHERE status = 'Pending'"

    Q_SELECT_UNNOTIFIED = """
        SELECT * FROM leave_requests
        WHERE employee_id = %s
          AND status IN ('Approved', 'Rejected')
          AND employee_notified = 0
        ORDER BY reviewed_at DESC
    """

    Q_MARK_NOTIFIED = "UPDATE leave_requests SET employee_notified = 1 WHERE id = %s"

    Q_MARK_ALL_NOTIFIED = """
        UPDATE leave_requests
        SET employee_notified = 1
        WHERE employee_id = %s AND status IN ('Approved', 'Rejected') AND employee_notified = 0
    """

