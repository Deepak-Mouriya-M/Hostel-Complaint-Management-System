import sqlite3
import hashlib
import datetime
import os
import getpass

DB_FILE = os.path.join(os.path.dirname(__file__), "hostel_complaints.db")

STATUS_PENDING = "Pending"
STATUS_IN_PROGRESS = "In Progress"
STATUS_RESOLVED = "Resolved"

PRIORITY_OPTIONS = ["Low", "Medium", "High"]


def db_connect():
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    with db_connect() as con:
        cur = con.cursor()

        # Drop old tables if they exist
        cur.executescript("""
DROP TABLE IF EXISTS Complaint_Update;
DROP TABLE IF EXISTS Complaint;
DROP TABLE IF EXISTS Complaint_Status;
DROP TABLE IF EXISTS Complaint_Type;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS Room;
DROP TABLE IF EXISTS Floor;
DROP TABLE IF EXISTS Hostel;
DROP TABLE IF EXISTS Warden;
DROP TABLE IF EXISTS Worker;
""")

        cur.executescript("""
CREATE TABLE Hostel (
    Hostel_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Hostel_Name TEXT,
    Hostel_Type TEXT,
    Floor INTEGER,
    Room_No INTEGER UNIQUE
);

CREATE TABLE Student (
    Student_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Student_Name TEXT,
    Username TEXT UNIQUE,
    Password TEXT,
    Room_No INTEGER
);

CREATE TABLE Warden (
    Warden_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Warden_Name TEXT,
    Warden_Ph_No TEXT,
    Username TEXT UNIQUE,
    Password TEXT
);

CREATE TABLE Worker (
    Worker_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Worker_Name TEXT,
    Worker_Ph_No TEXT,
    Work_Type TEXT,
    Username TEXT UNIQUE,
    Password TEXT
);

CREATE TABLE Admin (
    Admin_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Admin_Name TEXT,
    Username TEXT,
    Password TEXT
);

CREATE TABLE Complaint (
    Complaint_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Room_No INTEGER,
    Student_ID INTEGER,
    Worker_ID INTEGER,
    Warden_ID INTEGER,
    Admin_ID INTEGER,
    Problem_Type TEXT,
    Problem_Description TEXT,
    Status TEXT,
    Complaint_Date TEXT,
    Update_Date TEXT,
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
    FOREIGN KEY (Worker_ID) REFERENCES Worker(Worker_ID),
    FOREIGN KEY (Warden_ID) REFERENCES Warden(Warden_ID),
    FOREIGN KEY (Admin_ID) REFERENCES Admin(Admin_ID),
    FOREIGN KEY (Room_No) REFERENCES Hostel(Room_No)
);
""")

        # Insert sample data
        cur.executescript("""
INSERT INTO Hostel (Hostel_Name, Hostel_Type, Floor, Room_No) VALUES
('A Block','Boys',1,101),
('A Block','Boys',1,102),
('A Block','Boys',2,103),
('B Block','Girls',2,201),
('B Block','Girls',2,202),
('B Block','Girls',3,203),
('C Block','Boys',3,301),
('C Block','Boys',3,302),
('D Block','Girls',4,401),
('D Block','Girls',4,402);

INSERT INTO Student (Student_Name, Username, Password, Room_No) VALUES
('Arun','arun01','pass01',101),
('Vijay','vijay02','pass02',102),
('Rahul','rahul03','pass03',103),
('Meena','meena04','pass04',201),
('Priya','priya05','pass05',202),
('Divya','divya06','pass06',203),
('Karthik','karthik07','pass07',301),
('Ravi','ravi08','pass08',302),
('Anu','anu09','pass09',401),
('Sneha','sneha10','pass10',402);

INSERT INTO Warden (Warden_Name, Warden_Ph_No, Username, Password) VALUES
('Mr.Ravi','9876543210','warden1','pass1'),
('Ms.Latha','9876543211','warden2','pass2'),
('Mr.Kumar','9876543212','warden3','pass3'),
('Ms.Anitha','9876543213','warden4','pass4'),
('Mr.Selvam','9876543214','warden5','pass5');

INSERT INTO Worker (Worker_Name, Worker_Ph_No, Work_Type, Username, Password) VALUES
('Kumar','9001110001','Electrician','worker1','pass1'),
('Ramesh','9001110002','Plumber','worker2','pass2'),
('Suresh','9001110003','Carpenter','worker3','pass3'),
('Ganesh','9001110004','Cleaner','worker4','pass4'),
('Mani','9001110005','Technician','worker5','pass5');

INSERT INTO Admin (Admin_Name, Username, Password) VALUES
('System Admin','admin1','adminpass'),
('Super Admin','admin2','adminpass2');

INSERT INTO Complaint
(Problem_Type, Problem_Description, Status, Complaint_Date, Update_Date, Student_ID, Worker_ID, Warden_ID, Admin_ID, Room_No)
VALUES
('Electric Issue','Fan not working','Pending',date('now'),date('now'),1,1,1,1,101),
('Water Issue','No water supply','Assigned',date('now'),date('now'),2,2,1,1,102),
('Furniture Issue','Broken chair','Working in Progress',date('now'),date('now'),3,3,2,2,103),
('Electric Issue','Tube light not working','Completed',date('now'),date('now'),4,1,2,1,201),
('Plumbing Issue','Tap leakage','Pending',date('now'),date('now'),5,2,3,2,202),
('Cleaning Issue','Room not cleaned','Assigned',date('now'),date('now'),6,4,4,1,203),
('Network Issue','WiFi not working','Working in Progress',date('now'),date('now'),7,5,5,2,301);
""")

        con.commit()


def input_secure(prompt: str) -> str:
    try:
        return getpass.getpass(prompt)
    except Exception:
        return input(prompt)


def list_hostel_structure(con):
    cur = con.cursor()
    cur.execute("SELECT h.id as hid, h.name as hname, f.id as fid, f.name as fname, r.id as rid, r.room_number FROM Hostel h JOIN Floor f ON f.hostel_id = h.id JOIN Room r ON r.floor_id = f.id ORDER BY h.id,f.id,r.id")
    rows = cur.fetchall()
    last_h = last_f = None
    for row in rows:
        if row['hid'] != last_h:
            print(f"Hostel: {row['hname']} (id={row['hid']})")
            last_h = row['hid']
            last_f = None
        if row['fid'] != last_f:
            print(f"  Floor: {row['fname']} (id={row['fid']})")
            last_f = row['fid']
        print(f"    Room: {row['room_number']} (id={row['rid']})")


def register_student():
    with db_connect() as con:
        name = input("Student name: ").strip()
        email = input("Email: ").strip().lower()
        username = input("Choose username: ").strip()
        password = input_secure("Choose password: ").strip()
        password2 = input_secure("Confirm password: ").strip()
        if password != password2:
            print("Password mismatch. Aborting.")
            return

        print("Select your room from the available structure:")
        list_hostel_structure(con)
        hostel_id = int(input("Hostel ID: ").strip())
        floor_id = int(input("Floor ID: ").strip())
        room_id = int(input("Room ID: ").strip())

        cur = con.cursor()
        try:
            cur.execute("INSERT INTO Student (name,email,username,password_hash,hostel_id,floor_id,room_id) VALUES (?,?,?,?,?,?,?)",
                        (name, email, username, hash_password(password), hostel_id, floor_id, room_id))
            con.commit()
            print("Student registered successfully, please login.")
        except sqlite3.IntegrityError as e:
            print("Failed to register:", e)


def student_login():
    username = input("Username: ").strip()
    password = input_secure("Password: ").strip()
    with db_connect() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Student WHERE username = ?", (username,))
        student = cur.fetchone()
        if not student or student['password_hash'] != hash_password(password):
            print("Invalid student credentials")
            return None
        return dict(student)


def admin_login():
    username = input("Admin username: ").strip()
    password = input_secure("Password: ").strip()
    with db_connect() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Admin WHERE username = ?", (username,))
        admin = cur.fetchone()
        if not admin or admin['password_hash'] != hash_password(password):
            print("Invalid admin credentials")
            return None
        return dict(admin)


def submit_complaint(student):
    with db_connect() as con:
        cur = con.cursor()
        print("Complaint Types:")
        cur.execute("SELECT * FROM Complaint_Type")
        for row in cur.fetchall():
            print(f"{row['id']} - {row['name']}")

        type_id = int(input("Type ID: ").strip())
        print("Priority options: 1-Low,2-Medium,3-High")
        priority_index = int(input("Select priority (1/2/3): ").strip())
        if priority_index not in (1, 2, 3):
            print("Invalid priority")
            return
        priority = PRIORITY_OPTIONS[priority_index - 1]

        description = input("Describe the issue: ").strip()
        now = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')

        cur.execute("INSERT INTO Complaint (student_id, type_id, priority, description, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                    (student['id'], type_id, priority, description, now, now))
        complaint_id = cur.lastrowid
        cur.execute("SELECT id FROM Complaint_Status WHERE name = ?", (STATUS_PENDING,))
        status_id = cur.fetchone()[0]
        cur.execute("INSERT INTO Complaint_Update (complaint_id,status_id,admin_id,remark,updated_at) VALUES (?,?,?,?,?)",
                    (complaint_id, status_id, 0, 'Automatically set to Pending', now))
        con.commit()
        print(f"Complaint {complaint_id} submitted and marked as Pending.")


def view_student_complaints(student):
    with db_connect() as con:
        cur = con.cursor()
        cur.execute("SELECT c.*, ct.name as type_name, cs.name as status_name, a.name as assigned_admin_name FROM Complaint c JOIN Complaint_Type ct ON c.type_id = ct.id JOIN Complaint_Status cs ON c.status_id = cs.id LEFT JOIN Admin a ON c.assigned_admin_id = a.id WHERE c.student_id = ? ORDER BY c.created_at DESC", (student['id'],))
        rows = cur.fetchall()
        if not rows:
            print("No complaints submitted yet.")
            return
        for r in rows:
            print(f"ID:{r['id']} Type:{r['type_name']} Priority:{r['priority']} Status:{r['status_name']} Assigned:{r['assigned_admin_name'] or 'Unassigned'}")
            print(f"  Desc: {r['description']}")
            print(f"  Created: {r['created_at']} Updated: {r['updated_at']}")
            print("-")


def student_menu(student):
    while True:
        print(f"\nStudent: {student['name']} | {student['username']}")
        print("1. Submit complaint")
        print("2. View my complaints")
        print("3. Logout")
        choice = input("Choose: ").strip()
        if choice == '1':
            submit_complaint(student)
        elif choice == '2':
            view_student_complaints(student)
        elif choice == '3':
            break
        else:
            print("Invalid choice")


def list_complaints(admin):
    with db_connect() as con:
        cur = con.cursor()
        print("Filter by status (leave blank for all):")
        cur.execute("SELECT id,name FROM Complaint_Status")
        statuses = cur.fetchall()
        for s in statuses:
            print(f"{s['id']} - {s['name']}")
        f_status = input("Status ID: ").strip()

        print("Filter by type (leave blank for all):")
        cur.execute("SELECT id,name FROM Complaint_Type")
        types = cur.fetchall()
        for t in types:
            print(f"{t['id']} - {t['name']}")
        f_type = input("Type ID: ").strip()

        query = "SELECT c.*, ct.name as type_name, cs.name as status_name, s.name as student_name, a.name as assigned_admin_name FROM Complaint c JOIN Complaint_Type ct ON c.type_id = ct.id JOIN Complaint_Status cs ON c.status_id = cs.id JOIN Student s ON c.student_id = s.id LEFT JOIN Admin a ON c.assigned_admin_id = a.id"
        clauses = []
        args = []
        if f_status:
            clauses.append("c.status_id = ?")
            args.append(int(f_status))
        if f_type:
            clauses.append("c.type_id = ?")
            args.append(int(f_type))
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY c.created_at DESC"

        cur.execute(query, tuple(args))
        rows = cur.fetchall()
        if not rows:
            print("No complaints matching filters.")
            return []

        for r in rows:
            print(f"ID:{r['id']} Student:{r['student_name']} Type:{r['type_name']} Priority:{r['priority']} Status:{r['status_name']} Assigned:{r['assigned_admin_name'] or 'Unassigned'}")
            print(f"  Desc: {r['description']} (Created {r['created_at']} Updated {r['updated_at']})")
            print("-")
        return [r['id'] for r in rows]


def update_complaint(admin):
    complaint_ids = list_complaints(admin)
    if not complaint_ids:
        return
    selected = int(input("Choose complaint ID to update: ").strip())
    if selected not in complaint_ids:
        print("Not a valid complaint from list.")
        return

    with db_connect() as con:
        cur = con.cursor()

        print("Set status:")
        cur.execute("SELECT id,name FROM Complaint_Status")
        for s in cur.fetchall():
            print(f"{s['id']} - {s['name']}")
        status_id = int(input("Status ID: ").strip())

        assign = input("Assign to admin? (leave blank for no change) [id]: ").strip()
        assigned_id = None
        if assign:
            assigned_id = int(assign)

        remark = input("Remark message: ").strip()
        now = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')

        if assigned_id is not None:
            cur.execute("UPDATE Complaint SET status_id = ?, assigned_admin_id = ?, updated_at = ? WHERE id = ?",
                        (status_id, assigned_id, now, selected))
        else:
            cur.execute("UPDATE Complaint SET status_id = ?, updated_at = ? WHERE id = ?",
                        (status_id, now, selected))

        cur.execute("INSERT INTO Complaint_Update (complaint_id,status_id,admin_id,remark,updated_at) VALUES (?,?,?,?,?)",
                    (selected, status_id, admin['id'], remark or 'Updated by admin', now))
        con.commit()
        print(f"Complaint {selected} updated.")


def complaint_reports(admin):
    with db_connect() as con:
        cur = con.cursor()
        print("=== Summary Reports ===")
        cur.execute("SELECT cs.name AS status, COUNT(*) AS count FROM Complaint c JOIN Complaint_Status cs ON c.status_id = cs.id GROUP BY c.status_id")
        for row in cur.fetchall():
            print(f"Status {row['status']}: {row['count']}")

        cur.execute("SELECT priority, COUNT(*) AS count FROM Complaint GROUP BY priority")
        for row in cur.fetchall():
            print(f"Priority {row['priority']}: {row['count']}")

        cur.execute("SELECT ct.name AS type, COUNT(*) AS count FROM Complaint c JOIN Complaint_Type ct ON c.type_id = ct.id GROUP BY c.type_id")
        for row in cur.fetchall():
            print(f"Type {row['type']}: {row['count']}")


def admin_menu(admin):
    while True:
        print(f"\nAdmin: {admin['name']} | {admin['username']}")
        print("1. View/Filter complaints")
        print("2. Update a complaint")
        print("3. Reporting summary")
        print("4. Logout")
        choice = input("Choose: ").strip()
        if choice == '1':
            list_complaints(admin)
        elif choice == '2':
            update_complaint(admin)
        elif choice == '3':
            complaint_reports(admin)
        elif choice == '4':
            break
        else:
            print("Invalid choice")


def main_menu():
    init_db()
    while True:
        print("\nHostel Complaint Management System")
        print("1. Student login")
        print("2. Student register")
        print("3. Admin login")
        print("4. Exit")
        choice = input("Choose: ").strip()
        if choice == '1':
            student = student_login()
            if student:
                student_menu(student)
        elif choice == '2':
            register_student()
        elif choice == '3':
            admin = admin_login()
            if admin:
                admin_menu(admin)
        elif choice == '4':
            print("Goodbye")
            break
        else:
            print("Invalid choice")


if __name__ == '__main__':
    main_menu()
