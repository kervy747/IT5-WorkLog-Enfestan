-- Migration: Add late_considerations table
-- Date: February 22, 2026
-- Description: Creates table for employee late consideration requests

CREATE TABLE IF NOT EXISTS late_considerations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    attendance_date DATE NOT NULL,          -- The date of the late attendance
    reason TEXT NOT NULL,                    -- Why employee was late
    evidence_path VARCHAR(500) NULL,         -- Optional evidence file
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    reviewed_by INT NULL,                    -- Admin who reviewed
    reviewed_at DATETIME NULL,               -- When it was reviewed
    remarks TEXT NULL,                       -- Admin comments
    employee_notified TINYINT(1) DEFAULT 0,  -- Whether employee has been notified
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES employees(id),
    UNIQUE KEY unique_employee_date_late (employee_id, attendance_date)
);

-- Indexes for faster queries
CREATE INDEX idx_late_employee ON late_considerations(employee_id);
CREATE INDEX idx_late_date ON late_considerations(attendance_date);
CREATE INDEX idx_late_status ON late_considerations(status);
