-- Migration: Remove Staff role, absorb into Admin
-- Date: 2026-02-22
-- Description: Changes all Staff users to Admin and removes Staff from role ENUM

USE worklog_db;

-- Step 1: Update all Staff users to Admin
UPDATE users SET role = 'Admin' WHERE role = 'Staff';

-- Step 2: Alter the ENUM to remove Staff
ALTER TABLE users MODIFY COLUMN role ENUM('Admin', 'Employee') DEFAULT 'Employee';
