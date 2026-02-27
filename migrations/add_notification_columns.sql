-- Migration: Add employee_notified columns for notification system
-- Description: Tracks whether an employee has been notified about
--              their leave/overtime request approval or rejection

USE worklog_db;

-- Add employee_notified column to leave_requests
ALTER TABLE leave_requests 
ADD COLUMN IF NOT EXISTS employee_notified TINYINT(1) DEFAULT 0 
COMMENT 'Whether employee has been notified of the review result';

-- Add employee_notified column to overtime_requests
ALTER TABLE overtime_requests 
ADD COLUMN IF NOT EXISTS employee_notified TINYINT(1) DEFAULT 0 
COMMENT 'Whether employee has been notified of the review result';

-- Mark all existing reviewed requests as already notified
UPDATE leave_requests SET employee_notified = 1 WHERE status IN ('Approved', 'Rejected');
UPDATE overtime_requests SET employee_notified = 1 WHERE status IN ('Approved', 'Rejected');
