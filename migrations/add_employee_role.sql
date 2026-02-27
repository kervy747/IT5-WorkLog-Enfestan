-- Migration: Add 'Employee' to users.role ENUM
-- This adds the Employee role as a third distinct role alongside Admin and Staff
-- Run this on an existing database to apply the change

USE worklog_db;

-- Update ENUM to include 'Employee'
ALTER TABLE users
MODIFY COLUMN role ENUM('Admin', 'Staff', 'Employee') DEFAULT 'Employee';

-- Optionally update existing Staff users to Employee if desired:
-- UPDATE users SET role = 'Employee' WHERE role = 'Staff';
