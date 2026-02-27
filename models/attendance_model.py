"""
Attendance Model — Pure Blueprint (MVC)
Contains ONLY: TABLE name, FIELDS list, and SQL query constants.
Zero database imports. Zero query execution.
"""

class AttendanceModel:
    """Data structure, SQL query holder, and pure computation for attendance"""

    TABLE = 'attendance'

    FIELDS = [
        'id', 'employee_id', 'date', 'time_in', 'time_out',
        'lunch_start', 'lunch_end', 'total_time', 'lunch_duration',
        'paid_hours', 'overtime_hours', 'status', 'created_at', 'updated_at'
    ]

    # Standard working hours per day
    STANDARD_WORKING_HOURS = 8

    # ── SQL Query Constants ──
    Q_CHECK_IN = """
        INSERT INTO attendance (employee_id, date, time_in, status)
        VALUES (%s, %s, %s, 'Incomplete')
    """

    Q_START_LUNCH = """
        UPDATE attendance SET lunch_start = %s
        WHERE employee_id = %s AND date = %s
    """

    Q_END_LUNCH = """
        UPDATE attendance SET lunch_end = %s
        WHERE employee_id = %s AND date = %s
    """

    Q_CHECK_OUT = """
        UPDATE attendance
        SET time_out = %s, total_time = %s, lunch_duration = %s,
            paid_hours = %s, overtime_hours = %s, status = %s
        WHERE employee_id = %s AND date = %s
    """

    Q_GET_TODAY = "SELECT * FROM attendance WHERE employee_id = %s AND date = %s"

    Q_GET_EMPLOYEE = "SELECT * FROM attendance WHERE employee_id = %s ORDER BY date DESC"

    Q_GET_EMPLOYEE_RANGE = """
        SELECT * FROM attendance
        WHERE employee_id = %s AND date BETWEEN %s AND %s
        ORDER BY date DESC
    """

    Q_GET_ALL_BY_DATE = """
        SELECT a.*, e.employee_code, e.full_name, e.position, e.department,
               s.shift_name, s.start_time as shift_start, s.end_time as shift_end
        FROM attendance a
        INNER JOIN employees e ON a.employee_id = e.id
        LEFT JOIN shifts s ON e.shift_id = s.id
        WHERE a.date = %s
        ORDER BY a.time_in
    """

    Q_COUNT_PRESENT = "SELECT COUNT(*) as count FROM attendance WHERE date = %s"

    Q_COUNT_LATE = """
        SELECT COUNT(*) as count FROM attendance
        WHERE date = %s AND status LIKE '%%Late%%'
    """

    Q_COUNT_TOTAL_ACTIVE = "SELECT COUNT(*) as count FROM employees WHERE status = 'Active'"

    Q_GET_DEPARTMENT = """
        SELECT a.*, e.employee_code, e.full_name, e.position, e.department
        FROM attendance a
        INNER JOIN employees e ON a.employee_id = e.id
        WHERE e.department = %s AND a.date = %s
        ORDER BY a.time_in
    """

    Q_WEEKLY_SUMMARY = """
        SELECT a.date,
               COUNT(*) as present_count,
               SUM(CASE WHEN a.status LIKE '%%Late%%' THEN 1 ELSE 0 END) as late_count
        FROM attendance a
        WHERE a.date BETWEEN %s AND %s
        GROUP BY a.date
        ORDER BY a.date
    """

    # ── Employee-specific queries ──
    Q_GET_EMPLOYEE_LATE = """
        SELECT * FROM attendance
        WHERE employee_id = %s AND status LIKE '%%Late%%'
        ORDER BY date DESC
    """

    Q_GET_EMPLOYEE_STATS = """
        SELECT
            COUNT(*) as total_days,
            SUM(CASE WHEN status LIKE '%%On Time%%' THEN 1 ELSE 0 END) as on_time_days,
            SUM(CASE WHEN status LIKE '%%Late%%' THEN 1 ELSE 0 END) as late_days,
            SUM(CASE WHEN status LIKE '%%Complete%%' THEN 1 ELSE 0 END) as complete_days,
            SUM(CASE WHEN status LIKE '%%Undertime%%' THEN 1 ELSE 0 END) as undertime_days,
            COALESCE(SUM(paid_hours), 0) as total_paid_hours,
            COALESCE(AVG(paid_hours), 0) as avg_paid_hours
        FROM attendance
        WHERE employee_id = %s
    """

    Q_GET_EMPLOYEE_WEEKLY = """
        SELECT a.date,
               CASE WHEN a.status LIKE '%%Late%%' THEN 1 ELSE 0 END as is_late,
               CASE WHEN a.status LIKE '%%On Time%%' THEN 1 ELSE 0 END as is_on_time,
               a.paid_hours
        FROM attendance a
        WHERE a.employee_id = %s AND a.date BETWEEN %s AND %s
        ORDER BY a.date
    """

    Q_GET_EMPLOYEE_MONTHLY_SUMMARY = """
        SELECT
            DATE_FORMAT(date, '%%Y-%%m') as month,
            COUNT(*) as total_days,
            SUM(CASE WHEN status LIKE '%%Late%%' THEN 1 ELSE 0 END) as late_days,
            SUM(CASE WHEN status LIKE '%%On Time%%' THEN 1 ELSE 0 END) as on_time_days,
            COALESCE(SUM(paid_hours), 0) as total_paid_hours
        FROM attendance
        WHERE employee_id = %s
        GROUP BY DATE_FORMAT(date, '%%Y-%%m')
        ORDER BY month DESC
        LIMIT 6
    """
