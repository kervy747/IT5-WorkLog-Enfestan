"""Run migration to remove Staff role and absorb into Admin"""
import mysql.connector

conn = mysql.connector.connect(host='localhost', database='worklog_db', user='root', password='')
cursor = conn.cursor()

# Update Staff users to Admin
cursor.execute("UPDATE users SET role = 'Admin' WHERE role = 'Staff'")
print(f"Updated {cursor.rowcount} Staff users to Admin")

# Alter ENUM
cursor.execute("ALTER TABLE users MODIFY COLUMN role ENUM('Admin', 'Employee') DEFAULT 'Employee'")
conn.commit()
print("ENUM column updated successfully")

# Show current users
cursor.execute("SELECT u.username, u.role, e.full_name FROM users u JOIN employees e ON u.employee_id = e.id")
rows = cursor.fetchall()
print("\nCurrent users:")
for r in rows:
    print(f"  {r[0]:20s} {r[1]:10s} {r[2]}")

cursor.close()
conn.close()
