import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root', password='', database='worklog_db')
cur = conn.cursor(dictionary=True)
cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='worklog_db' AND TABLE_NAME='leave_requests' AND COLUMN_NAME='evidence_path'")
r = cur.fetchone()
if r:
    print("COLUMN EXISTS")
else:
    print("ADDING COLUMN...")
    cur.execute("ALTER TABLE leave_requests ADD COLUMN evidence_path VARCHAR(500) DEFAULT NULL")
    conn.commit()
    print("COLUMN ADDED")
cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='worklog_db' AND TABLE_NAME='leave_requests'")
cols = [row['COLUMN_NAME'] for row in cur.fetchall()]
print("ALL COLUMNS:", cols)
conn.close()
