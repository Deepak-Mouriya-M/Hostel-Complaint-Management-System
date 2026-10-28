import sqlite3, os
p='hostel_complaints.db'
if not os.path.exists(p):
    raise SystemExit('DB file not found: '+p)
con=sqlite3.connect(p)
cur=con.cursor()
print('=== Table counts:')
tables = ['Hostel','Student','Warden','Worker','Admin','Complaint']
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'{t}:',cur.fetchone()[0])
con.close()
