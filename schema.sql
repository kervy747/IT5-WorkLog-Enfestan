-- =====================================================
-- Work Log - Employee Attendance Monitoring System
-- MySQL Database Schema
-- =====================================================

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS worklog_db;
USE worklog_db;

-- =====================================================
-- Table: employees
-- Stores employee information
-- =====================================================
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_code VARCHAR(50) UNIQUE NOT NULL COMMENT 'Unique code for Check In/Check Out',
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    leave_credits INT DEFAULT 15 COMMENT 'Available leave credits',
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_employee_code (employee_code),
    INDEX idx_status (status),
    INDEX idx_department (department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: users
-- Stores user accounts for login
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL COMMENT 'SHA-256 hashed password',
    role ENUM('Admin', 'Employee') DEFAULT 'Employee',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: attendance
-- Stores daily attendance records
-- =====================================================
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    date DATE NOT NULL,
    time_in TIME,
    time_out TIME,
    lunch_start TIME COMMENT 'Lunch break start (UNPAID)',
    lunch_end TIME COMMENT 'Lunch break end',
    total_time DECIMAL(5,2) COMMENT 'Total time: time_out - time_in (hours)',
    lunch_duration DECIMAL(5,2) COMMENT 'Lunch duration: lunch_end - lunch_start (hours)',
    paid_hours DECIMAL(5,2) COMMENT 'Paid hours: total_time - lunch_duration',
    status VARCHAR(50) COMMENT 'On Time, Late, Complete, Undertime, Incomplete',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employee_date (employee_id, date),
    INDEX idx_date (date),
    INDEX idx_employee_date (employee_id, date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Sample Data for Testing
-- =====================================================

-- Insert sample employees
INSERT INTO employees (employee_code, full_name, position, department, email, phone, leave_credits, status) VALUES
('EMP001', 'John Doe', 'Software Engineer', 'IT', 'john.doe@company.com', '555-0101', 15, 'Active'),
('EMP002', 'Jane Smith', 'HR Manager', 'Human Resources', 'jane.smith@company.com', '555-0102', 15, 'Active'),
('EMP003', 'Mike Johnson', 'Accountant', 'Finance', 'mike.johnson@company.com', '555-0103', 15, 'Active'),
('EMP004', 'Sarah Williams', 'Marketing Specialist', 'Marketing', 'sarah.williams@company.com', '555-0104', 15, 'Active'),
('EMP005', 'Admin User', 'System Administrator', 'IT', 'admin@company.com', '555-0105', 15, 'Active');

-- Insert sample users
-- Password for all users: 'password123'
-- Hash: ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f
INSERT INTO users (employee_id, username, password_hash, role, is_active) VALUES
(1, 'john.doe', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Admin', 1),
(2, 'jane.smith', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Admin', 1),
(3, 'mike.johnson', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Admin', 1),
(4, 'sarah.williams', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Admin', 1),
(5, 'admin', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Admin', 1);

-- =====================================================
-- Views for Reporting
-- =====================================================

-- View: Daily attendance summary with employee details
CREATE OR REPLACE VIEW vw_daily_attendance AS
SELECT 
    a.id,
    a.date,
    e.employee_code,
    e.full_name,
    e.position,
    e.department,
    a.time_in,
    a.time_out,
    a.lunch_start,
    a.lunch_end,
    a.total_time,
    a.lunch_duration,
    a.paid_hours,
    a.status
FROM attendance a
INNER JOIN employees e ON a.employee_id = e.id
ORDER BY a.date DESC, a.time_in;

-- View: Employee attendance statistics
CREATE OR REPLACE VIEW vw_employee_stats AS
SELECT 
    e.id,
    e.employee_code,
    e.full_name,
    e.department,
    COUNT(a.id) as total_days,
    SUM(CASE WHEN a.status LIKE '%Complete%' THEN 1 ELSE 0 END) as complete_days,
    SUM(CASE WHEN a.status LIKE '%Late%' THEN 1 ELSE 0 END) as late_days,
    SUM(CASE WHEN a.status LIKE '%Undertime%' THEN 1 ELSE 0 END) as undertime_days,
    SUM(a.paid_hours) as total_paid_hours
FROM employees e
LEFT JOIN attendance a ON e.id = a.employee_id
WHERE e.status = 'Active'
GROUP BY e.id, e.employee_code, e.full_name, e.department;

-- =====================================================
-- End of Schema
-- =====================================================

-- Instructions:
-- 1. Make sure XAMPP MySQL is running
-- 2. Open phpMyAdmin (http://localhost/phpmyadmin)
-- 3. Create a new database named 'worklog_db' or import this file
-- 4. Run this SQL script to create tables and sample data
-- 5. Default login credentials:
--    Username: admin, Password: password123, Role: Admin
--    Username: john.doe, Password: password123, Role: Admin
