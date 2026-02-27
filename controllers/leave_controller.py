"""
Leave Controller (MVC)
Handles all leave request business logic and database operations.
"""

from datetime import datetime
from models.database import db
from models.leave_model import LeaveModel


class LeaveController:
    """Controller for leave request operations"""

    def __init__(self):
        self.db = db

    # ── CRUD Operations ──
    def create_leave_request(self, employee_id, leave_type, start_date, end_date,
                             days_count, reason, evidence_path=None):
        """Create a new leave request"""
        params = (employee_id, leave_type, start_date, end_date,
                  days_count, reason, evidence_path)
        if self.db.execute_query(LeaveModel.Q_INSERT, params):
            return self.db.get_last_insert_id()
        return None

    def get_pending_leaves(self):
        """Get all pending leave requests with employee info"""
        return self.db.fetch_all(LeaveModel.Q_SELECT_PENDING)

    def get_all_leaves(self, status=None):
        """Get all leave requests, optionally filtered by status"""
        if status:
            return self.db.fetch_all(LeaveModel.Q_SELECT_BY_STATUS, (status,))
        return self.db.fetch_all(LeaveModel.Q_SELECT_ALL)

    def get_employee_leaves(self, employee_id):
        """Get leave requests for a specific employee"""
        return self.db.fetch_all(LeaveModel.Q_SELECT_BY_EMPLOYEE, (employee_id,))

    def get_leave_by_id(self, leave_id):
        """Get a single leave request by ID"""
        return self.db.fetch_one(LeaveModel.Q_SELECT_BY_ID, (leave_id,))

    # ── Approval / Rejection ──
    def approve_leave(self, leave_id, reviewer_user_id, remarks=None):
        """
        Approve a leave request and deduct leave credits.

        Returns:
            (True, message) on success, (False, message) on failure
        """
        leave = self.db.fetch_one(LeaveModel.Q_SELECT_BY_ID, (leave_id,))
        if not leave:
            return False, "Leave request not found."

        # Check employee leave credits
        emp = self.db.fetch_one(LeaveModel.Q_SELECT_EMPLOYEE_CREDITS,
                                (leave['employee_id'],))
        if not emp:
            return False, "Employee not found."

        credits = int(emp.get('leave_credits') or 0)
        required = int(leave.get('days_count') or 0)
        if credits < required:
            return False, (f"Insufficient leave credits. "
                           f"Available: {credits}, "
                           f"Required: {required}")

        # Approve the request
        if not self.db.execute_query(LeaveModel.Q_APPROVE,
                                     (reviewer_user_id, remarks, leave_id)):
            return False, "Failed to approve leave request."

        # Deduct credits
        self.db.execute_query(LeaveModel.Q_DEDUCT_CREDITS,
                              (leave['days_count'], leave['employee_id']))

        return True, "Leave request approved successfully."

    def reject_leave(self, leave_id, reviewer_user_id, remarks=None):
        """Reject a leave request"""
        if self.db.execute_query(LeaveModel.Q_REJECT,
                                 (reviewer_user_id, remarks, leave_id)):
            return True, "Leave request rejected."
        return False, "Failed to reject leave request."

    # ── Statistics ──
    def get_pending_count(self):
        """Get count of pending leave requests"""
        result = self.db.fetch_one(LeaveModel.Q_COUNT_PENDING)
        return result['count'] if result else 0

    def get_employee_credits(self, employee_id):
        """Get leave credits for an employee"""
        result = self.db.fetch_one(LeaveModel.Q_SELECT_EMPLOYEE_CREDITS,
                                   (employee_id,))
        return result['leave_credits'] if result else 0

    # ── Notification Methods ──
    def get_unnotified_reviews(self, employee_id):
        """Get leave requests reviewed but not yet notified to employee"""
        return self.db.fetch_all(LeaveModel.Q_SELECT_UNNOTIFIED, (employee_id,))

    def mark_as_notified(self, leave_id):
        """Mark a leave request as notified"""
        return self.db.execute_query(LeaveModel.Q_MARK_NOTIFIED, (leave_id,))

    def mark_all_notified(self, employee_id):
        """Mark all reviewed leave requests as notified for an employee"""
        return self.db.execute_query(LeaveModel.Q_MARK_ALL_NOTIFIED, (employee_id,))
