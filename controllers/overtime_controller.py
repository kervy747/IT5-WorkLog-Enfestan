"""
Overtime Controller (MVC)
Handles all overtime request business logic and database operations.
"""

from datetime import datetime
from models.database import db
from models.overtime_model import OvertimeModel


class OvertimeController:
    """Controller for overtime request operations"""

    def __init__(self):
        self.db = db

    # ── CRUD Operations ──
    def create_request(self, employee_id, request_date, hours_requested, reason):
        """Create a new overtime request"""
        params = (employee_id, request_date, hours_requested, reason)
        if self.db.execute_query(OvertimeModel.Q_INSERT, params):
            return self.db.get_last_insert_id()
        return None

    def get_pending_requests(self):
        """Get all pending overtime requests with employee info"""
        return self.db.fetch_all(OvertimeModel.Q_SELECT_PENDING)

    def get_all_requests(self):
        """Get all overtime requests with employee and reviewer info"""
        return self.db.fetch_all(OvertimeModel.Q_SELECT_ALL)

    def get_employee_requests(self, employee_id):
        """Get overtime requests for a specific employee"""
        return self.db.fetch_all(OvertimeModel.Q_SELECT_BY_EMPLOYEE, (employee_id,))

    def get_request_by_id(self, request_id):
        """Get a single overtime request by ID"""
        return self.db.fetch_one(OvertimeModel.Q_SELECT_BY_ID, (request_id,))

    # ── Approval / Rejection ──
    def approve_request(self, request_id, reviewer_id, remarks=None):
        """Approve an overtime request"""
        params = (reviewer_id, datetime.now(), remarks, request_id)
        return self.db.execute_query(OvertimeModel.Q_APPROVE, params)

    def reject_request(self, request_id, reviewer_id, remarks=None):
        """Reject an overtime request"""
        params = (reviewer_id, datetime.now(), remarks, request_id)
        return self.db.execute_query(OvertimeModel.Q_REJECT, params)

    # ── Overtime Tracking ──
    def get_approved_for_date(self, employee_id, check_date):
        """Check if employee has approved overtime for a specific date"""
        return self.db.fetch_one(OvertimeModel.Q_SELECT_APPROVED_FOR_DATE,
                                 (employee_id, check_date))

    def update_actual_overtime(self, request_id, actual_hours):
        """Update actual overtime hours worked"""
        return self.db.execute_query(OvertimeModel.Q_UPDATE_ACTUAL,
                                     (actual_hours, request_id))

    # ── Statistics ──
    def get_pending_count(self):
        """Get count of pending overtime requests"""
        result = self.db.fetch_one(OvertimeModel.Q_COUNT_PENDING)
        return result['count'] if result else 0

    def has_pending_request(self, employee_id, request_date):
        """Check if employee already has a pending request for a date"""
        result = self.db.fetch_one(OvertimeModel.Q_HAS_PENDING,
                                   (employee_id, request_date))
        return result['count'] > 0 if result else False

    def get_monthly_overtime(self, employee_id, year, month):
        """Get total overtime hours for an employee in a specific month"""
        result = self.db.fetch_one(OvertimeModel.Q_MONTHLY_OVERTIME,
                                   (employee_id, year, month))
        return float(result.get('total_overtime') or 0) if result else 0

    # ── Notification Methods ──
    def get_unnotified_reviews(self, employee_id):
        """Get overtime requests reviewed but not yet notified to employee"""
        return self.db.fetch_all(OvertimeModel.Q_SELECT_UNNOTIFIED, (employee_id,))

    def mark_as_notified(self, request_id):
        """Mark an overtime request as notified"""
        return self.db.execute_query(OvertimeModel.Q_MARK_NOTIFIED, (request_id,))

    def mark_all_notified(self, employee_id):
        """Mark all reviewed overtime requests as notified for an employee"""
        return self.db.execute_query(OvertimeModel.Q_MARK_ALL_NOTIFIED, (employee_id,))
