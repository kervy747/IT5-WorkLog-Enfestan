-- Migration: Add shifts table and shift_id to employees
-- Run this in phpMyAdmin or MySQL command line

-- Create shifts table
CREATE TABLE IF NOT EXISTS shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shift_name VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    work_hours DECIMAL(4,2) DEFAULT 8.00,
    grace_period_mins INT DEFAULT 15,
    min_hours_before_lunch DECIMAL(4,2) DEFAULT 3.00,
    is_default BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default shifts
INSERT INTO shifts (shift_name, start_time, end_time, work_hours, grace_period_mins, min_hours_before_lunch, is_default) VALUES
('Regular', '08:00:00', '17:00:00', 8.00, 15, 3.00, 1),
('Morning', '06:00:00', '15:00:00', 8.00, 15, 3.00, 0),
('Mid', '09:00:00', '18:00:00', 8.00, 15, 3.00, 0),
('Night', '22:00:00', '07:00:00', 8.00, 15, 3.00, 0);

-- Add shift_id column to employees table
ALTER TABLE employees ADD COLUMN shift_id INT DEFAULT 1;

-- Add foreign key constraint
ALTER TABLE employees ADD CONSTRAINT fk_employee_shift 
    FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE SET NULL;

-- Update existing employees to use Regular shift (id=1)
UPDATE employees SET shift_id = 1 WHERE shift_id IS NULL;
