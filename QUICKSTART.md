# Work Log - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install XAMPP
1. Download XAMPP from https://www.apachefriends.org/
2. Install XAMPP to `C:\xampp`
3. Open XAMPP Control Panel
4. Click **Start** next to **MySQL**

### Step 2: Create Database
1. Open browser and go to: http://localhost/phpmyadmin
2. Click **Import** tab
3. Click **Choose File** and select `schema.sql` from this folder
4. Click **Go** button at the bottom
5. You should see "Import has been successfully finished"

### Step 3: Install Python Packages
Open Command Prompt in this folder and run:
```
pip install -r requirements.txt
```

### Step 4: Run the Application
Double-click `run.bat` or run in command prompt:
```
python main.py
```

## 🔐 Login Credentials

### Admin Account
- **Username:** admin
- **Password:** password123
- **Role:** Admin

### Additional Admin Account (Test)
- **Username:** john.doe
- **Password:** password123
- **Role:** Admin

## 📖 How to Use

### As Employee:

1. **Login** with employee credentials
2. **Check In** when you start work
3. **Start Lunch** when you begin lunch break
4. **End Lunch** when you return from lunch
5. **Check Out** when you finish work
6. View your attendance history in the table

### As Administrator:

1. **Login** with admin credentials
2. **Monitor** real-time attendance on dashboard
3. **Manage Employees:**
   - Add new employees
   - Edit employee information
   - Update leave credits
4. **Generate Reports:**
   - Daily attendance reports
   - Department reports
   - Individual employee reports
5. **Export** reports to CSV

## 🕐 Time Calculation

**Important:** The system calculates paid hours as follows:

```
Paid Hours = (Check Out - Check In) - Lunch Duration
```

**Example:**
- Check In: 8:00 AM
- Start Lunch: 12:00 PM
- End Lunch: 1:00 PM
- Check Out: 5:00 PM

**Calculation:**
- Total Time: 9 hours (5 PM - 8 AM)
- Lunch: 1 hour (1 PM - 12 PM)
- **Paid Hours: 8 hours** (9 - 1)

**Note:** Short breaks (15 min × 2) are PAID and NOT deducted!

## 🎨 Features Overview

### Employee Features
- ✅ Secure login
- ✅ Check In/Out with one click
- ✅ Lunch break tracking
- ✅ Real-time clock
- ✅ Personal attendance history
- ✅ Automatic status calculation

### Admin Features
- ✅ Full system access
- ✅ Employee management
- ✅ Attendance monitoring
- ✅ Report generation
- ✅ CSV export
- ✅ Leave credits management

## 🐛 Troubleshooting

### "Database connection failed"
**Solution:**
1. Make sure XAMPP is running
2. Check MySQL is started in XAMPP Control Panel
3. Import `schema.sql` in phpMyAdmin

### "Module not found: PyQt6"
**Solution:**
```
pip install PyQt6
```

### "Logo not showing"
**Solution:**
Create the logo by running:
```
python assets/create_logo.py
```

### Application won't start
**Solution:**
1. Run setup check: `python setup_check.py`
2. Fix any issues reported
3. Make sure all requirements are installed

## 📞 Need Help?

1. Check the full **README.md** for detailed documentation
2. Run **setup_check.py** to diagnose issues
3. Review the console output for error messages

## 🎯 Next Steps

1. ✅ Test the application with default credentials
2. ✅ Add your own employees through Admin panel
3. ✅ Create user accounts for new employees
4. ✅ Replace the default logo with your company logo
5. ✅ Customize shift start time if needed (in attendance_model.py)

---

**Enjoy using Work Log!** 🎉
