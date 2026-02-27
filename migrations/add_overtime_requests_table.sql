-- Migration: Add overtime_requests table
-- Date: January 25, 2026
-- Description: Creates table for overtime pre-approval system

CREATE TABLE IF NOT EXISTS overtime_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    request_date DATE NOT NULL,           -- Date when overtime will be worked
    hours_requested DECIMAL(4,2) NOT NULL, -- How many OT hours requested
    reason TEXT NOT NULL,                  -- Why overtime is needed
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    reviewed_by INT NULL,                  -- Admin who reviewed
    reviewed_at DATETIME NULL,             -- When it was reviewed
    remarks TEXT NULL,                     -- Admin comments
    actual_overtime DECIMAL(4,2) NULL,     -- Actual OT hours worked (filled after checkout)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (reviewed_by) REFERENCES employees(id)
);

-- Add overtime_hours column to attendance table if not exists
ALTER TABLE attendance ADD COLUMN IF NOT EXISTS overtime_hours DECIMAL(4,2) DEFAULT 0;

-- Index for faster queries
CREATE INDEX idx_overtime_employee ON overtime_requests(employee_id);
CREATE INDEX idx_overtime_date ON overtime_requests(request_date);
CREATE INDEX idx_overtime_status ON overtime_requests(status);
