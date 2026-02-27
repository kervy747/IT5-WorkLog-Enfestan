"""
Attendance Controller (MVC)
Handles attendance check-in, lunch breaks, and check-out operations.
All DB operations via Database singleton using model SQL constants.
Zero UI imports. Returns result tuples for the view to display.
"""

from datetime import datetime, date, timedelta, time as time_type
from models.database import db
from models.attendance_model import AttendanceModel
from models.shift_model import ShiftModel


class AttendanceController:
    """Controller for attendance operations  pure transaction, zero UI"""

    def __init__(self, employee_id):
        self.employee_id = employee_id
        self.db = db

    #  Read Operations 
    def get_today_record(self):
        return self.db.fetch_one(AttendanceModel.Q_GET_TODAY,
                                 (self.employee_id, date.today()))

    def get_today_attendance(self):
        return self.get_today_record()

    def get_attendance_history(self, start_date=None, end_date=None):
        if start_date and end_date:
            return self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE_RANGE,
                                     (self.employee_id, start_date, end_date))
        return self.db.fetch_all(AttendanceModel.Q_GET_EMPLOYEE,
                                 (self.employee_id,))

    #  Shift Helper 
    def _get_employee_shift(self):
        shift = self.db.fetch_one(ShiftModel.Q_SELECT_EMPLOYEE_SHIFT,
                                  (self.employee_id,))
        if not shift:
            shift = self.db.fetch_one(ShiftModel.Q_SELECT_DEFAULT)
        if not shift:
            shift = self.db.fetch_one(ShiftModel.Q_SELECT_FIRST_ACTIVE)
        return shift

    #  Check-In 
    def can_check_in(self):
        """
        Validate if check-in is possible.
        Returns (can, title, message, msg_type)
        """
        if datetime.now().weekday() == 6:
            return (False, "Sunday - No Work Day",
                    "Check-in is disabled on Sundays. Enjoy your rest day!", "warning")

        today_record = self.get_today_record()
        if today_record:
            return (False, "Already Checked In",
                    "You have already checked in today.", "warning")

        # Validate check-in is within shift schedule
        shift = self._get_employee_shift()
        if shift:
            now = datetime.now()
            shift_end = shift.get('end_time')
            shift_start = shift.get('start_time')
            shift_name = shift.get('shift_name', 'your shift')

            def to_time(val):
                if isinstance(val, timedelta):
                    total_seconds = int(val.total_seconds())
                    h = total_seconds // 3600
                    m = (total_seconds % 3600) // 60
                    s = total_seconds % 60
                    return time_type(h, m, s)
                elif isinstance(val, str):
                    return datetime.strptime(val, '%H:%M:%S').time()
                return val

            try:
                end_t = to_time(shift_end)
                start_t = to_time(shift_start)
                current_t = now.time()

                # Determine if the employee is outside their shift window
                outside = False
                if start_t < end_t:
                    # Day shift (e.g. 8 AM – 5 PM): block after end
                    outside = current_t > end_t
                else:
                    # Night shift (e.g. 10 PM – 7 AM): block in the gap
                    # Gap is between end_t and start_t (e.g. 7 AM – 10 PM)
                    outside = end_t < current_t < start_t

                if outside:
                    end_fmt = datetime.combine(date.today(), end_t).strftime('%I:%M %p')
                    start_fmt = datetime.combine(date.today(), start_t).strftime('%I:%M %p')
                    return (False, "Outside Shift Schedule",
                            f"Your shift ({shift_name}) is {start_fmt} - {end_fmt}.\n"
                            f"Check-in is not allowed after your shift has ended.",
                            "warning")
            except (ValueError, TypeError):
                pass  # If shift time parsing fails, allow check-in

        return (True, "", "", "")

    def check_in(self):
        """
        Execute check-in. Call can_check_in() first for validation.
        Returns (success, title, message, msg_type)
        """
        now = datetime.now()
        params = (self.employee_id, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S'))
        success = self.db.execute_query(AttendanceModel.Q_CHECK_IN, params)

        if success:
            current_time = now.strftime('%I:%M %p')
            return (True, "Check In Successful",
                    f"Checked in at {current_time}", "info")
        return (False, "Check In Failed",
                "Failed to record check-in. Please try again.", "error")

    #  Lunch 
    def can_start_lunch(self):
        """
        Check if employee can start lunch based on shift rules.
        Returns (can, title, message, msg_type)
        """
        today_record = self.get_today_record()
        if not today_record:
            return (False, "Not Checked In", "Please check in first.", "warning")
        if today_record.get('lunch_start'):
            return (False, "Lunch Already Started", "Lunch already started.", "warning")
        if today_record.get('time_out'):
            return (False, "Already Checked Out", "Already checked out.", "warning")

        shift = self._get_employee_shift()
        min_hours = float(shift.get('min_hours_before_lunch') or 3) if shift else 3.0

        time_in = today_record.get('time_in')
        if time_in:
            today_date = date.today()
            if isinstance(time_in, timedelta):
                total_seconds = int(time_in.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                dt_in = datetime.combine(today_date, time_type(hours, minutes, seconds))
            elif isinstance(time_in, datetime):
                dt_in = time_in
            else:
                dt_in = datetime.combine(today_date, time_in)

            earliest_lunch = dt_in + timedelta(hours=min_hours)
            now = datetime.now()
            if now < earliest_lunch:
                remaining = earliest_lunch - now
                mins_left = int(remaining.total_seconds() / 60)
                return (False, "Cannot Start Lunch Yet",
                        f"You need to work at least {min_hours:.0f} hours before lunch.\n"
                        f"Earliest lunch: {earliest_lunch.strftime('%I:%M %p')}\n"
                        f"({mins_left} minutes remaining)", "warning")

        return (True, "", "", "")

    def start_lunch(self):
        """
        Record lunch start. Call can_start_lunch() first for validation.
        Returns (success, title, message, msg_type)
        """
        now = datetime.now()
        params = (now.strftime('%H:%M:%S'), self.employee_id, now.strftime('%Y-%m-%d'))
        success = self.db.execute_query(AttendanceModel.Q_START_LUNCH, params)

        if success:
            return (True, "Lunch Started",
                    f"Lunch break started at {now.strftime('%I:%M %p')}", "info")
        return (False, "Failed",
                "Failed to record lunch start. Please try again.", "error")

    def can_end_lunch(self):
        """
        Validate if lunch end is possible.
        Returns (can, title, message, msg_type)
        """
        today_record = self.get_today_record()
        if not today_record:
            return (False, "Not Checked In", "Please check in first.", "warning")
        if not today_record.get('lunch_start'):
            return (False, "Lunch Not Started",
                    "Please start lunch first before ending it.", "warning")
        if today_record.get('lunch_end'):
            return (False, "Lunch Already Ended",
                    "You have already ended your lunch break.", "warning")
        return (True, "", "", "")

    def end_lunch(self):
        """
        Record lunch end. Call can_end_lunch() first for validation.
        Returns (success, title, message, msg_type)
        """
        now = datetime.now()
        params = (now.strftime('%H:%M:%S'), self.employee_id, now.strftime('%Y-%m-%d'))
        success = self.db.execute_query(AttendanceModel.Q_END_LUNCH, params)

        if success:
            return (True, "Lunch Ended",
                    f"Lunch break ended at {now.strftime('%I:%M %p')}", "info")
        return (False, "Failed",
                "Failed to record lunch end. Please try again.", "error")

    #  Check-Out 
    def can_check_out(self):
        """
        Validate if check-out is possible.
        Returns (can, title, message, msg_type)
        """
        today_record = self.get_today_record()
        if not today_record:
            return (False, "Not Checked In",
                    "You have not checked in today.", "warning")
        if today_record.get('time_out'):
            return (False, "Already Checked Out",
                    "You have already checked out today.", "warning")
        return (True, "", "", "")

    def check_out(self):
        """
        Execute check-out with time calculations.
        Returns (success, title, message, msg_type)
        """
        today_record = self.get_today_record()
        if not today_record:
            return (False, "Not Checked In",
                    "You have not checked in today.", "warning")
        if today_record.get('time_out'):
            return (False, "Already Checked Out",
                    "You have already checked out today.", "warning")

        now = datetime.now()
        time_in = today_record.get('time_in')
        lunch_start = today_record.get('lunch_start')
        lunch_end = today_record.get('lunch_end')

        # compute paid hours
        result = AttendanceController.compute_paid_hours(
            time_in, now.strftime('%H:%M:%S'), lunch_start, lunch_end
        )
        total_time = result['total_time']
        lunch_duration = result['lunch_duration']
        paid_hours = result['paid_hours']

        # Determine overtime
        overtime_hours = max(0, round(paid_hours - AttendanceModel.STANDARD_WORKING_HOURS, 2))

        # Determine status
        shift = self._get_employee_shift()
        shift_start = shift.get('start_time', '08:00:00') if shift else '08:00:00'
        grace_period = int(shift.get('grace_period_mins') or 15) if shift else 15
        status = AttendanceController.determine_status(time_in, paid_hours, shift_start, grace_period)

        params = (
            now.strftime('%H:%M:%S'), total_time, lunch_duration,
            paid_hours, overtime_hours, status,
            self.employee_id, now.strftime('%Y-%m-%d')
        )
        success = self.db.execute_query(AttendanceModel.Q_CHECK_OUT, params)

        if success:
            current_time = now.strftime('%I:%M %p')
            return (True, "Check Out Successful",
                    f"Checked out at {current_time}\n"
                    f"Paid Hours: {paid_hours:.2f}\n"
                    f"Status: {status}", "info")
        return (False, "Check Out Failed",
                "Failed to record check-out. Please try again.", "error")

    # ── Pure Computation Methods ──
    @staticmethod
    def compute_paid_hours(time_in, time_out, lunch_start, lunch_end):
        """
        Calculate paid working hours.

        BUSINESS RULE:
        - Two 15-minute breaks are PAID (not deducted)
        - Only lunch break (1 hour) is UNPAID (deducted)

        Returns:
            Dictionary with total_time, lunch_duration, and paid_hours in hours
        """
        today = date.today()

        def to_datetime(value):
            if value is None:
                return None
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                t = datetime.strptime(value, '%H:%M:%S').time()
                return datetime.combine(today, t)
            if isinstance(value, timedelta):
                total_seconds = int(value.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                t = time_type(hours, minutes, seconds)
                return datetime.combine(today, t)
            else:
                return datetime.combine(today, value)

        dt_in = to_datetime(time_in)
        dt_out = to_datetime(time_out)

        if dt_in is None or dt_out is None:
            return {'total_time': 0, 'lunch_duration': 0, 'paid_hours': 0}

        total_time_delta = dt_out - dt_in
        total_hours = total_time_delta.total_seconds() / 3600

        lunch_hours = 0
        if lunch_start and lunch_end:
            dt_lunch_start = to_datetime(lunch_start)
            dt_lunch_end = to_datetime(lunch_end)
            lunch_delta = dt_lunch_end - dt_lunch_start
            lunch_hours = lunch_delta.total_seconds() / 3600

        paid_hours = total_hours - lunch_hours

        return {
            'total_time': round(total_hours, 2),
            'lunch_duration': round(lunch_hours, 2),
            'paid_hours': round(paid_hours, 2)
        }

    @staticmethod
    def determine_status(time_in, paid_hours, shift_start_time='08:00:00', grace_period_mins=15):
        """
        Determine attendance status.

        Returns:
            Status string e.g. "On Time, Complete" or "Late, Undertime"
        """
        status = []

        if isinstance(time_in, datetime):
            check_in_time = time_in.time()
        elif isinstance(time_in, timedelta):
            total_seconds = int(time_in.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            check_in_time = time_type(hours, minutes, seconds)
        else:
            check_in_time = time_in

        if isinstance(shift_start_time, timedelta):
            total_seconds = int(shift_start_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            shift_start = time_type(hours, minutes, seconds)
        elif isinstance(shift_start_time, str):
            shift_start = datetime.strptime(shift_start_time, '%H:%M:%S').time()
        else:
            shift_start = shift_start_time

        shift_start_dt = datetime.combine(date.today(), shift_start)
        grace_end_dt = shift_start_dt + timedelta(minutes=int(grace_period_mins))
        grace_end = grace_end_dt.time()

        if check_in_time > grace_end:
            status.append("Late")
        else:
            status.append("On Time")

        if paid_hours >= AttendanceModel.STANDARD_WORKING_HOURS:
            status.append("Complete")
        else:
            status.append("Undertime")

        return ", ".join(status)
