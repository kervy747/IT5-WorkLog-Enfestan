"""
Shift Controller (MVC)
Handles all shift management business logic and database operations.
"""

from datetime import datetime
from models.database import db
from models.shift_model import ShiftModel


class ShiftController:
    """Controller for shift management operations"""

    def __init__(self):
        self.db = db

    # ── Read Operations ──
    def get_all_shifts(self, include_inactive=False):
        """Get all shifts, optionally including inactive"""
        if include_inactive:
            return self.db.fetch_all(ShiftModel.Q_SELECT_ALL)
        return self.db.fetch_all(ShiftModel.Q_SELECT_ALL_ACTIVE)

    def get_shift_by_id(self, shift_id):
        """Get a shift by ID"""
        return self.db.fetch_one(ShiftModel.Q_SELECT_BY_ID, (shift_id,))

    def get_default_shift(self):
        """Get the default shift, with fallback to first active shift"""
        result = self.db.fetch_one(ShiftModel.Q_SELECT_DEFAULT)
        if not result:
            result = self.db.fetch_one(ShiftModel.Q_SELECT_FIRST_ACTIVE)
        return result

    def get_employee_shift(self, employee_id):
        """Get shift assigned to an employee, with fallback to default"""
        result = self.db.fetch_one(ShiftModel.Q_SELECT_EMPLOYEE_SHIFT,
                                   (employee_id,))
        if not result:
            return self.get_default_shift()
        return result

    # ── Create / Update / Delete ──
    def create_shift(self, shift_name, start_time, end_time, work_hours=8.0,
                     grace_period_mins=15, min_hours_before_lunch=3.0, is_default=False):
        """Create a new shift"""
        if is_default:
            self.db.execute_query(ShiftModel.Q_UNSET_ALL_DEFAULTS)

        params = (shift_name, start_time, end_time, work_hours,
                  grace_period_mins, min_hours_before_lunch, is_default)
        if self.db.execute_query(ShiftModel.Q_INSERT, params):
            return self.db.get_last_insert_id()
        return None

    def update_shift(self, shift_id, shift_name, start_time, end_time,
                     work_hours=8.0, grace_period_mins=15,
                     min_hours_before_lunch=3.0, is_default=False):
        """Update an existing shift"""
        if is_default:
            self.db.execute_query(ShiftModel.Q_UNSET_DEFAULTS_EXCEPT, (shift_id,))

        params = (shift_name, start_time, end_time, work_hours,
                  grace_period_mins, min_hours_before_lunch, is_default, shift_id)
        return self.db.execute_query(ShiftModel.Q_UPDATE, params)

    def delete_shift(self, shift_id):
        """
        Delete (deactivate) a shift.
        Returns (success, message) tuple.
        """
        result = self.db.fetch_one(ShiftModel.Q_COUNT_EMPLOYEES, (shift_id,))
        if result and result['count'] > 0:
            return False, f"Cannot delete shift — {result['count']} employee(s) assigned."

        if self.db.execute_query(ShiftModel.Q_DEACTIVATE, (shift_id,)):
            return True, "Shift deleted successfully."
        return False, "Cannot delete the default shift."

    # ── Utility ──
    @staticmethod
    def format_shift_display(shift):
        """Format shift for display — e.g. 'Regular (8:00 AM - 5:00 PM)'."""
        if not shift:
            return "No Shift"

        def format_time(time_val):
            if time_val is None:
                return "N/A"
            if isinstance(time_val, str):
                time_obj = datetime.strptime(time_val, '%H:%M:%S')
            else:
                # timedelta from database
                total_seconds = int(time_val.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                time_obj = datetime.strptime(f"{hours:02d}:{minutes:02d}:00", '%H:%M:%S')
            return time_obj.strftime('%I:%M %p').lstrip('0')

        start = format_time(shift['start_time'])
        end = format_time(shift['end_time'])
        return f"{shift['shift_name']} ({start} - {end})"

    def get_employees_count(self, shift_id):
        """Get count of active employees assigned to a shift"""
        result = self.db.fetch_one(ShiftModel.Q_COUNT_EMPLOYEES, (shift_id,))
        return result['count'] if result else 0

    def reassign_employees(self, from_shift_id, to_shift_id):
        """Reassign all employees from one shift to another"""
        return self.db.execute_query(ShiftModel.Q_REASSIGN_EMPLOYEES,
                                     (to_shift_id, from_shift_id))
