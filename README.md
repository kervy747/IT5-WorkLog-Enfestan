# Work Log - Employee Attendance Monitoring System

A comprehensive desktop application for tracking employee attendance with automated time calculation and reporting capabilities.

![Work Log Logo](assets/logo.png)

## 📋 Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Business Rules](#business-rules)
- [Default Credentials](#default-credentials)
- [Usage Guide](#usage-guide)

## ✨ Features

### Staff Features
- ✅ Secure login with role-based authentication
- ✅ Check In / Check Out functionality
- ✅ Lunch break tracking (Start/End)
- ✅ Real-time clock display
- ✅ Personal attendance history
- ✅ Daily statistics dashboard
- ✅ Automatic paid hours calculation

### Admin Features
- ✅ Complete system oversight
- ✅ View all employee attendance
- ✅ Employee management (Add/Edit/Deactivate)
- ✅ Leave credits management
- ✅ Generate reports by:
  - Daily attendance
  - Department
  - Individual employee
- ✅ Export reports to CSV/PDF
- ✅ Real-time attendance monitoring

## 🛠️ Technology Stack

- **Language:** Python 3.x
- **GUI Framework:** PyQt6
- **Database:** MySQL (via XAMPP)
- **Database Connector:** mysql-connector-python
- **Architecture:** MVC (Model-View-Controller)

## 📁 Project Structure

```
worklog/
│
├── models/                      # Data models and business logic
│   ├── database.py             # Database connection manager
│   ├── employee_model.py       # Employee CRUD operations
│   ├── user_model.py           # User authentication
│   └── attendance_model.py     # Attendance tracking and calculations
│
├── views/                       # PyQt6 UI components
│   ├── login_view.py           # Login screen
│   ├── staff_dashboard_view.py # Staff dashboard
│   └── admin_dashboard_view.py # Admin dashboard
│
├── controllers/                 # Application logic
│   ├── login_controller.py     # Login handling
│   ├── attendance_controller.py # Attendance operations
│   ├── staff_dashboard_controller.py
│   ├── admin_dashboard_controller.py
│   ├── employee_controller.py  # Employee management
│   └── reports_controller.py   # Report generation
│
├── assets/                      # Images and resources
│   └── logo.png                # Official Work Log logo
│
├── styles/                      # Application styling
│   └── theme.qss               # Color scheme stylesheet
│
├── schema.sql                   # Database schema
├── main.py                      # Application entry point
└── README.md                    # This file
```

## 💻 Installation

### Prerequisites

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)

2. **XAMPP** (for MySQL database)
   - Download from [apachefriends.org](https://www.apachefriends.org/)

### Step 1: Clone or Download the Project

```bash
cd c:\worklog
```

### Step 2: Install Python Dependencies

```bash
pip install PyQt6
pip install mysql-connector-python
pip install Pillow  # For logo creation (optional)
```

Or use requirements.txt (if created):
```bash
pip install -r requirements.txt
```

### Step 3: Create the Logo (Optional)

```bash
cd assets
python create_logo.py
```

Or place your own `logo.png` in the `assets/` folder.

## 🗄️ Database Setup

### Step 1: Start XAMPP

1. Open XAMPP Control Panel
2. Start **Apache** and **MySQL** services

### Step 2: Create Database

1. Open phpMyAdmin: [http://localhost/phpmyadmin](http://localhost/phpmyadmin)
2. Click on "Import" tab
3. Choose `schema.sql` from the project folder
4. Click "Go" to import

Alternatively, run the SQL file directly:
```sql
-- Copy and paste the contents of schema.sql into phpMyAdmin SQL tab
```

### Step 3: Verify Database

Check that the following tables exist in `worklog_db`:
- ✅ employees
- ✅ users
- ✅ attendance

## 🚀 Running the Application

```bash
python main.py
```

The login window will appear with the Work Log logo.

## 📖 Business Rules

### Working Time Policy

**Two (2) Short Breaks: 15 minutes each**
- These are **PAID** breaks
- **NOT** deducted from working hours
- Optional to record (for monitoring only)

**One (1) Lunch Break: 1 hour**
- This is **UNPAID**
- **MUST** be deducted from working hours

### Time Calculation Formula

```
total_time = time_out - time_in
lunch_duration = lunch_end - lunch_start
paid_hours = total_time - lunch_duration

Standard working hours = 8 hours/day
```

**Important:** Only lunch time is deducted. Short breaks are NOT subtracted.

### Status Rules

- **On Time:** Check-in at or before shift start (default: 08:00 AM)
- **Late:** Check-in after shift start time
- **Complete:** Paid hours ≥ 8 hours
- **Undertime:** Paid hours < 8 hours
- **Incomplete:** No check-out recorded

## 🔐 Default Credentials

### Admin Account
```
Username: admin
Password: password123
Role: Admin
```

### Staff Accounts
```
Username: john.doe
Password: password123
Role: Staff

Username: jane.smith
Password: password123
Role: Staff
```

## 📚 Usage Guide

### For Staff

1. **Login**
   - Enter username and password
   - Select "Staff" role
   - Click "Login"

2. **Check In**
   - Click "Check In" button
   - Time is automatically recorded

3. **Lunch Break**
   - Click "Start Lunch" when beginning lunch
   - Click "End Lunch" when returning

4. **Check Out**
   - Click "Check Out" at end of day
   - Paid hours automatically calculated
   - Status automatically determined

5. **View Records**
   - Your attendance history is displayed in the table
   - Shows Date, Time In, Time Out, Paid Hours, and Status

### For Admin

1. **Login**
   - Enter username and password
   - Select "Admin" role
   - Click "Login"

2. **Monitor Attendance**
   - View today's attendance in real-time
   - See Present, Late, and Absent counts
   - Filter by date

3. **Manage Employees**
   - Add new employees
   - Edit employee information
   - Update leave credits
   - Deactivate employees

4. **Generate Reports**
   - Select report type (Daily/Department/Employee)
   - Choose date range
   - Export to CSV or PDF

## 🎨 Color Scheme

The application uses a professional color palette:

- **Primary Blue:** #5A8AC4 (Headers, primary actions)
- **Success Green:** #89E4F7 (Present, success states)
- **Warning Yellow:** #FFD107 (Late, warnings)
- **Danger Red:** #FC4A5A (Absent, errors)
- **Background:** #F5F5F5 (Page background)
- **Text:** #333440 (Primary text)
- **Muted:** #687280 (Secondary text)

## 🔧 Configuration

### Database Connection

Edit `models/database.py` to change database credentials:

```python
def connect(self, host='localhost', database='worklog_db', 
            user='root', password=''):
```

### Shift Start Time

Edit `models/attendance_model.py` to change default shift start:

```python
def determine_status(time_in, paid_hours, shift_start_time='08:00:00'):
```

## 📝 Sample Usage Scenario

**John Doe's Typical Day:**

1. **8:00 AM** - Checks in (Status: On Time)
2. **12:00 PM** - Starts lunch
3. **1:00 PM** - Ends lunch (1 hour lunch recorded)
4. **5:00 PM** - Checks out

**Calculation:**
- Total Time: 5:00 PM - 8:00 AM = 9 hours
- Lunch Duration: 1:00 PM - 12:00 PM = 1 hour
- Paid Hours: 9 - 1 = **8 hours**
- Status: **On Time, Complete**

## 🐛 Troubleshooting

### Database Connection Failed
- Ensure XAMPP MySQL is running
- Check database name is `worklog_db`
- Verify credentials in `models/database.py`

### Logo Not Showing
- Ensure `logo.png` exists in `assets/` folder
- Run `python assets/create_logo.py` to generate default logo

### Import Error: PyQt6
```bash
pip install --upgrade PyQt6
```

### Import Error: mysql.connector
```bash
pip install mysql-connector-python
```

## 📄 License

This project is for educational and internal use.

## 👥 Support

For questions or issues, please contact the development team.

---

**Work Log** - Making attendance tracking simple and efficient! ✨
