"""
Staff Dashboard Controller (MVC)
Handles staff dashboard operations — all DB via Database singleton.
"""

from datetime import date, datetime, timedelta
from models.database import db
from models.attendance_model import AttendanceModel
from models.employee_model import EmployeeModel
from models.leave_model import LeaveModel
from models.overtime_model import OvertimeModel
from models.shift_model import ShiftModel
from models.late_consideration_model import LateConsiderationModel
from controllers.shift_controller import ShiftController


class StaffDashboardController:
    """Controller for staff dashboard"""

    def __init__(self, employee_id):
        self.employee_id = employee_id
        self.db = db

    # ── Dashboard Statistics ──
    def get_daily_statistics(self, target_date=None):
        if target_date is None:
            target_date = date.today()

        all_employees = self.db.fetch_all(EmployeeModel.Q_SELECT_NON_ADMIN)
        total = len(all_employees)
        attendance = self.db.fetch_all(AttendanceModel.Q_GET_ALL_BY_DATE, (target_date,))
        present = len(attendance)
        late = sum(1 for r in attendance
                   if r.get('status') and 'Late' in str(r.get('status', '')))

        approved_leaves = self.db.fetch_all(LeaveModel.Q_SELECT_BY_STATUS, ('Approved',))
        on_leave = 0
        for leave in approved_leaves:
            start = leave.get('start_date')
            end = leave.get('end_date')
            if start and end and start <= target_date <= end:
                on_leave += 1

        absent = max(0, total - present - on_leave)
        return {
            'total': total, 'present': present, 'late': late,
            'absent': absent, 'on_leave': on_leave
        }

    # ── My Attendance ──
    def get_my_attendance_records(self, limit=30):
        records = self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE,
                                    (self.employee_id,))
        return records[:limit] if records else []

    def get_today_attendance(self):
        return self.db.fetch_one(AttendanceModel.Q_GET_TODAY,
                                 (self.employee_id, date.today()))

    # ── Employee Data ──
    def get_all_employees(self):
        return self.db.fetch_all(EmployeeModel.Q_SELECT_ALL)

    def get_non_admin_employees(self):
        return self.db.fetch_all(EmployeeModel.Q_SELECT_NON_ADMIN)

    def get_employee_by_id(self, employee_id):
        return self.db.fetch_one(EmployeeModel.Q_SELECT_BY_ID, (employee_id,))

    # ── Attendance (all employees) ──
    def get_all_attendance(self, target_date=None):
        if target_date is None:
            target_date = date.today()
        return self.db.fetch_all(AttendanceModel.Q_GET_ALL_BY_DATE, (target_date,))

    # ── Leave Management ──
    def get_all_leaves(self, status=None):
        if status:
            return self.db.fetch_all(LeaveModel.Q_SELECT_BY_STATUS, (status,))
        return self.db.fetch_all(LeaveModel.Q_SELECT_ALL)

    def approve_leave(self, leave_id, reviewer_user_id, remarks=None):
        leave = self.db.fetch_one(LeaveModel.Q_SELECT_BY_ID, (leave_id,))
        if not leave:
            return False
        emp = self.db.fetch_one(LeaveModel.Q_SELECT_EMPLOYEE_CREDITS,
                                (leave['employee_id'],))
        if not emp or int(emp.get('leave_credits') or 0) < int(leave.get('days_count') or 0):
            return False
        if not self.db.execute_query(LeaveModel.Q_APPROVE,
                                     (reviewer_user_id, remarks, leave_id)):
            return False
        self.db.execute_query(LeaveModel.Q_DEDUCT_CREDITS,
                              (leave['days_count'], leave['employee_id']))
        return True

    def reject_leave(self, leave_id, reviewer_user_id, remarks=None):
        return self.db.execute_query(LeaveModel.Q_REJECT,
                                     (reviewer_user_id, remarks, leave_id))

    # ── Overtime Management ──
    def get_all_overtime_requests(self):
        return self.db.fetch_all(OvertimeModel.Q_SELECT_ALL)

    def get_pending_overtime_requests(self):
        return self.db.fetch_all(OvertimeModel.Q_SELECT_PENDING)

    def approve_overtime(self, request_id, reviewer_employee_id, remarks=None):
        params = (reviewer_employee_id, datetime.now(), remarks, request_id)
        return self.db.execute_query(OvertimeModel.Q_APPROVE, params)

    def reject_overtime(self, request_id, reviewer_employee_id, remarks=None):
        params = (reviewer_employee_id, datetime.now(), remarks, request_id)
        return self.db.execute_query(OvertimeModel.Q_REJECT, params)

    # ── Shift ──
    def get_employee_shift(self, employee_id):
        result = self.db.fetch_one(ShiftModel.Q_SELECT_EMPLOYEE_SHIFT, (employee_id,))
        if not result:
            result = self.db.fetch_one(ShiftModel.Q_SELECT_DEFAULT)
        if not result:
            result = self.db.fetch_one(ShiftModel.Q_SELECT_FIRST_ACTIVE)
        return result

    def get_all_shifts(self):
        return self.db.fetch_all(ShiftModel.Q_SELECT_ALL_ACTIVE)

    def get_shift_by_id(self, shift_id):
        return self.db.fetch_one(ShiftModel.Q_SELECT_BY_ID, (shift_id,))

    @staticmethod
    def format_shift_display(shift):
        return ShiftController.format_shift_display(shift)

    # ── Chart Data ──
    def get_weekly_attendance_summary(self):
        """Get daily attendance counts for the last 7 days."""
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        return self.db.fetch_all(AttendanceModel.Q_WEEKLY_SUMMARY,
                                 (start_date, end_date))

    # ── Employee Leave/OT Requests ──
    def get_employee_leaves(self, employee_id):
        return self.db.fetch_all(LeaveModel.Q_SELECT_BY_EMPLOYEE, (employee_id,))

    def get_employee_overtime_requests(self, employee_id):
        return self.db.fetch_all(OvertimeModel.Q_SELECT_BY_EMPLOYEE, (employee_id,))

    def create_leave_request(self, employee_id, leave_type, start_date, end_date,
                             reason, evidence_path=None):
        days_count = (end_date - start_date).days + 1
        params = (employee_id, leave_type, start_date, end_date,
                  days_count, reason, evidence_path)
        return self.db.execute_query(LeaveModel.Q_INSERT, params)

    def create_overtime_request(self, employee_id, request_date, hours_requested, reason):
        params = (employee_id, request_date, hours_requested, reason)
        return self.db.execute_query(OvertimeModel.Q_INSERT, params)

    def has_pending_overtime(self, employee_id, request_date):
        result = self.db.fetch_one(OvertimeModel.Q_HAS_PENDING,
                                   (employee_id, request_date))
        return result['count'] > 0 if result else False

    def get_approved_overtime_for_date(self, employee_id, request_date):
        return self.db.fetch_one(OvertimeModel.Q_SELECT_APPROVED_FOR_DATE,
                                 (employee_id, request_date))

    # ── Notifications ──
    def get_unnotified_leave_reviews(self, employee_id):
        return self.db.fetch_all(LeaveModel.Q_SELECT_UNNOTIFIED, (employee_id,))

    def get_unnotified_overtime_reviews(self, employee_id):
        return self.db.fetch_all(OvertimeModel.Q_SELECT_UNNOTIFIED, (employee_id,))

    def mark_all_leaves_notified(self, employee_id):
        return self.db.execute_query(LeaveModel.Q_MARK_ALL_NOTIFIED, (employee_id,))

    def mark_all_overtime_notified(self, employee_id):
        return self.db.execute_query(OvertimeModel.Q_MARK_ALL_NOTIFIED, (employee_id,))

    def get_employee_credits(self, employee_id):
        result = self.db.fetch_one(LeaveModel.Q_SELECT_EMPLOYEE_CREDITS, (employee_id,))
        return result['leave_credits'] if result else 0

    # ── Late Consideration Requests ──
    def get_all_late_considerations(self):
        return self.db.fetch_all(LateConsiderationModel.Q_SELECT_ALL)

    def get_pending_late_considerations(self):
        return self.db.fetch_all(LateConsiderationModel.Q_SELECT_PENDING)

    def get_employee_late_considerations(self, employee_id):
        return self.db.fetch_all(LateConsiderationModel.Q_SELECT_BY_EMPLOYEE, (employee_id,))

    def create_late_consideration(self, employee_id, attendance_date, reason, evidence_path=None):
        params = (employee_id, attendance_date, reason, evidence_path)
        return self.db.execute_query(LateConsiderationModel.Q_INSERT, params)

    def has_pending_late_consideration(self, employee_id, attendance_date):
        result = self.db.fetch_one(LateConsiderationModel.Q_HAS_PENDING,
                                   (employee_id, attendance_date))
        return result['count'] > 0 if result else False

    def approve_late_consideration(self, request_id, reviewer_employee_id, remarks=None):
        params = (reviewer_employee_id, datetime.now(), remarks, request_id)
        return self.db.execute_query(LateConsiderationModel.Q_APPROVE, params)

    def reject_late_consideration(self, request_id, reviewer_employee_id, remarks=None):
        params = (reviewer_employee_id, datetime.now(), remarks, request_id)
        return self.db.execute_query(LateConsiderationModel.Q_REJECT, params)

    def get_unnotified_late_consideration_reviews(self, employee_id):
        return self.db.fetch_all(LateConsiderationModel.Q_SELECT_UNNOTIFIED, (employee_id,))

    def mark_all_late_considerations_notified(self, employee_id):
        return self.db.execute_query(LateConsiderationModel.Q_MARK_ALL_NOTIFIED, (employee_id,))

    # ── Employee Late Records ──
    def get_employee_late_records(self, employee_id):
        return self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE_LATE, (employee_id,))

    # ── Employee Personal Analytics ──
    def get_employee_stats(self, employee_id):
        return self.db.fetch_one(AttendanceModel.Q_GET_EMPLOYEE_STATS, (employee_id,))

    def get_employee_weekly_data(self, employee_id):
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        return self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE_WEEKLY,
                                 (employee_id, start_date, end_date))

    def get_employee_monthly_summary(self, employee_id):
        return self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE_MONTHLY_SUMMARY,
                                 (employee_id,))

    # ── Display Formatting (pure, no DB) ──
    @staticmethod
    def format_time(time_value):
        if time_value:
            if hasattr(time_value, 'strftime'):
                return time_value.strftime('%I:%M %p')
            else:
                return str(time_value)
        return '-'

    @staticmethod
    def format_hours(hours_value):
        if hours_value is not None:
            return f"{hours_value:.2f}"
        return '-'
