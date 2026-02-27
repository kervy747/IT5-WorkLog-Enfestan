"""
Admin Dashboard Controller (MVC)
Handles admin dashboard operations — all DB via Database singleton.
"""

from datetime import date, datetime, timedelta
from models.database import db
from models.attendance_model import AttendanceModel
from models.employee_model import EmployeeModel
from models.leave_model import LeaveModel
from models.overtime_model import OvertimeModel
from models.late_consideration_model import LateConsiderationModel
from models.shift_model import ShiftModel
from controllers.shift_controller import ShiftController


class AdminDashboardController:
    """Controller for admin dashboard"""

    def __init__(self):
        self.db = db

    # ── Attendance ──
    def get_daily_statistics(self, target_date=None):
        if target_date is None:
            target_date = date.today()

        all_employees = self.db.fetch_all(EmployeeModel.Q_SELECT_NON_ADMIN)
        total = len(all_employees)
        attendance = self.db.fetch_all(AttendanceModel.Q_GET_ALL_BY_DATE, (target_date,))
        present = len(attendance)
        late = sum(1 for r in attendance
                   if r.get('status') and 'Late' in str(r.get('status', '')))

        # On-leave today
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

    def get_all_attendance(self, target_date=None):
        if target_date is None:
            target_date = date.today()
        return self.db.fetch_all(AttendanceModel.Q_GET_ALL_BY_DATE, (target_date,))

    def get_department_attendance(self, department, target_date=None):
        if target_date is None:
            target_date = date.today()
        return self.db.fetch_all(AttendanceModel.Q_GET_DEPARTMENT,
                                 (department, target_date))

    def get_employee_attendance(self, employee_id, start_date=None, end_date=None):
        if start_date and end_date:
            return self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE_RANGE,
                                     (employee_id, start_date, end_date))
        return self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE, (employee_id,))

    # ── Employees ──
    def get_all_employees(self):
        return self.db.fetch_all(EmployeeModel.Q_SELECT_ALL)

    def get_active_employees(self):
        return self.db.fetch_all(EmployeeModel.Q_SELECT_ACTIVE)

    def get_non_admin_employees(self):
        return self.db.fetch_all(EmployeeModel.Q_SELECT_NON_ADMIN)

    def get_employee_by_id(self, employee_id):
        return self.db.fetch_one(EmployeeModel.Q_SELECT_BY_ID, (employee_id,))

    # ── Leave Management ──
    def get_all_leaves(self, status=None):
        if status:
            return self.db.fetch_all(LeaveModel.Q_SELECT_BY_STATUS, (status,))
        return self.db.fetch_all(LeaveModel.Q_SELECT_ALL)

    def get_pending_leaves(self):
        return self.db.fetch_all(LeaveModel.Q_SELECT_PENDING)

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

    def get_pending_leave_count(self):
        result = self.db.fetch_one(LeaveModel.Q_COUNT_PENDING)
        return result['count'] if result else 0

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

    def get_pending_overtime_count(self):
        result = self.db.fetch_one(OvertimeModel.Q_COUNT_PENDING)
        return result['count'] if result else 0

    # ── Late Consideration Management ──
    def get_all_late_considerations(self):
        return self.db.fetch_all(LateConsiderationModel.Q_SELECT_ALL)

    def get_pending_late_considerations(self):
        return self.db.fetch_all(LateConsiderationModel.Q_SELECT_PENDING)

    def approve_late_consideration(self, request_id, reviewer_employee_id, remarks=None):
        params = (reviewer_employee_id, datetime.now(), remarks, request_id)
        return self.db.execute_query(LateConsiderationModel.Q_APPROVE, params)

    def reject_late_consideration(self, request_id, reviewer_employee_id, remarks=None):
        params = (reviewer_employee_id, datetime.now(), remarks, request_id)
        return self.db.execute_query(LateConsiderationModel.Q_REJECT, params)

    def get_pending_late_count(self):
        result = self.db.fetch_one(LateConsiderationModel.Q_COUNT_PENDING)
        return result['count'] if result else 0

    def get_late_consideration_by_id(self, request_id):
        return self.db.fetch_one(LateConsiderationModel.Q_SELECT_BY_ID, (request_id,))

    # ── Shift Management ──
    def get_all_shifts(self):
        return self.db.fetch_all(ShiftModel.Q_SELECT_ALL_ACTIVE)

    def get_shift_by_id(self, shift_id):
        return self.db.fetch_one(ShiftModel.Q_SELECT_BY_ID, (shift_id,))

    def get_employee_shift(self, employee_id):
        result = self.db.fetch_one(ShiftModel.Q_SELECT_EMPLOYEE_SHIFT, (employee_id,))
        if not result:
            result = self.db.fetch_one(ShiftModel.Q_SELECT_DEFAULT)
        if not result:
            result = self.db.fetch_one(ShiftModel.Q_SELECT_FIRST_ACTIVE)
        return result

    def get_employees_count_by_shift(self, shift_id):
        result = self.db.fetch_one(ShiftModel.Q_COUNT_EMPLOYEES, (shift_id,))
        return result['count'] if result else 0

    def create_shift(self, name, start_time, end_time, work_hours=8.0,
                     grace_period_mins=15, min_hours_before_lunch=3.0, is_default=False):
        if is_default:
            self.db.execute_query(ShiftModel.Q_UNSET_ALL_DEFAULTS)
        params = (name, start_time, end_time, work_hours,
                  grace_period_mins, min_hours_before_lunch, is_default)
        if self.db.execute_query(ShiftModel.Q_INSERT, params):
            return self.db.get_last_insert_id()
        return None

    def update_shift(self, shift_id, name, start_time, end_time, work_hours=8.0,
                     grace_period_mins=15, min_hours_before_lunch=3.0, is_default=False):
        if is_default:
            self.db.execute_query(ShiftModel.Q_UNSET_DEFAULTS_EXCEPT, (shift_id,))
        params = (name, start_time, end_time, work_hours,
                  grace_period_mins, min_hours_before_lunch, is_default, shift_id)
        return self.db.execute_query(ShiftModel.Q_UPDATE, params)

    def delete_shift(self, shift_id):
        result = self.db.fetch_one(ShiftModel.Q_COUNT_EMPLOYEES, (shift_id,))
        if result and result['count'] > 0:
            return False
        return self.db.execute_query(ShiftModel.Q_DEACTIVATE, (shift_id,))

    # ── Shift Display Utility ──
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
