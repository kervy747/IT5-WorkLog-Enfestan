"""Run migration to add employee_notified column - outputs to file"""
import mysql.connector
import sys

results = []

conn = mysql.connector.connect(host='localhost', user='root', password='', database='worklog_db')
cur = conn.cursor()

# Add column to leave_requests if not exists
try:
    cur.execute("ALTER TABLE leave_requests ADD COLUMN employee_notified TINYINT(1) DEFAULT 0")
    conn.commit()
    results.append("Added employee_notified to leave_requests")
except Exception as e:
    if "Duplicate" in str(e):
        results.append("leave_requests already has employee_notified")
    else:
        results.append(f"Error leave: {e}")

# Add column to overtime_requests if not exists
try:
    cur.execute("ALTER TABLE overtime_requests ADD COLUMN employee_notified TINYINT(1) DEFAULT 0")
    conn.commit()
    results.append("Added employee_notified to overtime_requests")
except Exception as e:
    if "Duplicate" in str(e):
        results.append("overtime_requests already has employee_notified")
    else:
        results.append(f"Error ot: {e}")

# Mark existing reviewed records as notified
cur.execute("UPDATE leave_requests SET employee_notified = 1 WHERE status IN ('Approved', 'Rejected')")
conn.commit()
results.append(f"Updated {cur.rowcount} leave_requests")

cur.execute("UPDATE overtime_requests SET employee_notified = 1 WHERE status IN ('Approved', 'Rejected')")
conn.commit()
results.append(f"Updated {cur.rowcount} overtime_requests")

conn.close()
results.append("Migration complete!")

# Write to file
with open("c:/worklog/migration_result.txt", "w") as f:
    f.write("\n".join(results))
