import streamlit as st
import sqlite3
import datetime
import hashlib
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "hostel_complaints.db")

@st.cache_resource
def get_connection():
    con = sqlite3.connect(DB_FILE, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def load_user(username, password, table, id_col, name_col):
    con = get_connection(); cur = con.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE Username = ?", (username,))
    user = cur.fetchone()
    if user and user['Password'] == password:  # Note: passwords are plain in the sample data
        return user
    return None

def get_students():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM Student")
    return cur.fetchall()

def get_wardens():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM Warden")
    return cur.fetchall()

def get_workers():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM Worker")
    return cur.fetchall()

def get_admins():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT * FROM Admin")
    return cur.fetchall()

def get_hostels():
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT DISTINCT Hostel_Name FROM Hostel ORDER BY Hostel_Name")
    return [row[0] for row in cur.fetchall()]


def get_rooms_for_hostel(hostel_name):
    con = get_connection(); cur = con.cursor()
    cur.execute("SELECT Room_No FROM Hostel WHERE Hostel_Name = ? ORDER BY Room_No", (hostel_name,))
    return [row[0] for row in cur.fetchall()]


def register_student():
    st.header("Student Registration")
    name = st.text_input("Full Name", key="reg_name")
    username = st.text_input("Username", key="reg_username")
    password = st.text_input("Password", type='password', key="reg_password")
    confirm_password = st.text_input("Confirm Password", type='password', key="reg_confirm_password")
    st.write("Select your hostel from the list and type your room number.")
    hostels = get_hostels()
    hostel_name = st.selectbox("Hostel", hostels, key="reg_hostel") if hostels else None
    room_no = st.text_input("Room No", key="reg_room")

    if st.button("Create Account", key="reg_create"):
        if not name or not username or not password or not confirm_password:
            st.error("All fields are required.")
            return
        if password != confirm_password:
            st.error("Passwords do not match.")
            return
        if room_no is None:
            st.error("Please choose an available room.")
            return

        con = get_connection(); cur = con.cursor()
        try:
            cur.execute(
                "INSERT INTO Student (Student_Name, Username, Password, Room_No) VALUES (?, ?, ?, ?)",
                (name.strip(), username.strip(), password, room_no)
            )
            con.commit()
            st.success("Account created successfully. You can now log in.")
        except sqlite3.IntegrityError:
            st.error("Username is already taken. Please choose a different username.")


def get_complaints():
    con = get_connection(); cur = con.cursor()
    cur.execute("""
SELECT c.*, s.Student_Name, w.Worker_Name, wd.Warden_Name, a.Admin_Name
FROM Complaint c
LEFT JOIN Student s ON c.Student_ID = s.Student_ID
LEFT JOIN Worker w ON c.Worker_ID = w.Worker_ID
LEFT JOIN Warden wd ON c.Warden_ID = wd.Warden_ID
LEFT JOIN Admin a ON c.Admin_ID = a.Admin_ID
ORDER BY c.Complaint_Date DESC
""")
    return cur.fetchall()

def student_login():
    st.header("Student Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        user = load_user(username, password, "Student", "Student_ID", "Student_Name")
        if user:
            st.session_state['user'] = user
            st.session_state['role'] = 'student'
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Invalid credentials")

def warden_login():
    st.header("Warden Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        user = load_user(username, password, "Warden", "Warden_ID", "Warden_Name")
        if user:
            st.session_state['user'] = user
            st.session_state['role'] = 'warden'
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Invalid credentials")

def worker_login():
    st.header("Worker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        user = load_user(username, password, "Worker", "Worker_ID", "Worker_Name")
        if user:
            st.session_state['user'] = user
            st.session_state['role'] = 'worker'
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Invalid credentials")

def admin_login():
    st.header("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        user = load_user(username, password, "Admin", "Admin_ID", "Admin_Name")
        if user:
            st.session_state['user'] = user
            st.session_state['role'] = 'admin'
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Invalid credentials")

def student_dashboard():
    user = st.session_state['user']
    st.sidebar.write(f"Logged in as Student: {user['Student_Name']}")
    page = st.sidebar.selectbox("Menu", ["Submit Complaint", "My Complaints", "Logout"])
    
    if page == "Submit Complaint":
        st.header("Submit a Complaint")
        problem_type = st.selectbox("Problem Type", ["Electric Issue", "Water Issue", "Furniture Issue", "Plumbing Issue", "Cleaning Issue", "Network Issue"])
        description = st.text_area("Description")
        if st.button("Submit"):
            con = get_connection(); cur = con.cursor()
            now = datetime.date.today().isoformat()
            cur.execute("""
INSERT INTO Complaint (Room_No, Student_ID, Problem_Type, Problem_Description, Status, Complaint_Date, Update_Date)
VALUES (?, ?, ?, ?, 'Pending', ?, ?)
""", (user['Room_No'], user['Student_ID'], problem_type, description, now, now))
            con.commit()
            st.success("Complaint submitted successfully")
    
    elif page == "My Complaints":
        st.header("My Complaints")
        con = get_connection(); cur = con.cursor()
        cur.execute("SELECT * FROM Complaint WHERE Student_ID = ? ORDER BY Complaint_Date DESC", (user['Student_ID'],))
        complaints = cur.fetchall()
        for c in complaints:
            st.write(f"ID: {c['Complaint_ID']}, Type: {c['Problem_Type']}, Status: {c['Status']}, Date: {c['Complaint_Date']}")
            st.write(f"Description: {c['Problem_Description']}")
            st.write("---")
    
    else:
        st.session_state.clear()
        st.rerun()

def warden_dashboard():
    user = st.session_state['user']
    st.sidebar.write(f"Logged in as Warden: {user['Warden_Name']}")
    page = st.sidebar.selectbox("Menu", ["View Complaints", "Update Status", "Logout"])
    
    if page == "View Complaints":
        st.header("All Complaints")
        complaints = get_complaints()
        for c in complaints:
            st.write(f"ID: {c['Complaint_ID']}, Student: {c['Student_Name']}, Room: {c['Room_No']}, Type: {c['Problem_Type']}, Status: {c['Status']}")
            st.write(f"Description: {c['Problem_Description']}")
            st.write("---")
    
    elif page == "Update Status":
        st.header("Update Complaint Status")
        complaint_id = st.number_input("Complaint ID", min_value=1, step=1)
        new_status = st.selectbox("New Status", ["Pending", "Assigned", "Working in Progress", "Completed"])
        if st.button("Update"):
            con = get_connection(); cur = con.cursor()
            now = datetime.date.today().isoformat()
            cur.execute("UPDATE Complaint SET Status = ?, Update_Date = ?, Warden_ID = ? WHERE Complaint_ID = ?", (new_status, now, user['Warden_ID'], complaint_id))
            con.commit()
            st.success("Status updated")
    
    else:
        st.session_state.clear()
        st.rerun()

def worker_dashboard():
    user = st.session_state['user']
    st.sidebar.write(f"Logged in as Worker: {user['Worker_Name']} ({user['Work_Type']})")
    page = st.sidebar.selectbox("Menu", ["My Complaints", "Update Status", "Logout"])
    
    if page == "My Complaints":
        st.header("Assigned Complaints")
        con = get_connection(); cur = con.cursor()
        cur.execute("""
SELECT c.*, s.Student_Name FROM Complaint c
JOIN Student s ON c.Student_ID = s.Student_ID
WHERE c.Worker_ID = ? ORDER BY c.Complaint_Date DESC
""", (user['Worker_ID'],))
        complaints = cur.fetchall()
        for c in complaints:
            st.write(f"ID: {c['Complaint_ID']}, Student: {c['Student_Name']}, Room: {c['Room_No']}, Type: {c['Problem_Type']}, Status: {c['Status']}")
            st.write(f"Description: {c['Problem_Description']}")
            st.write("---")
    
    elif page == "Update Status":
        st.header("Update Complaint Status")
        complaint_id = st.number_input("Complaint ID", min_value=1, step=1)
        new_status = st.selectbox("New Status", ["Pending", "Assigned", "Working in Progress", "Completed"])
        if st.button("Update"):
            con = get_connection(); cur = con.cursor()
            now = datetime.date.today().isoformat()
            cur.execute("UPDATE Complaint SET Status = ?, Update_Date = ? WHERE Complaint_ID = ? AND Worker_ID = ?", (new_status, now, complaint_id, user['Worker_ID']))
            con.commit()
            st.success("Status updated")
    
    else:
        st.session_state.clear()
        st.rerun()

def admin_dashboard():
    user = st.session_state['user']
    st.sidebar.write(f"Logged in as Admin: {user['Admin_Name']}")
    page = st.sidebar.selectbox("Menu", ["All Complaints", "Assign/Remove Workers", "Reports", "Logout"])
    
    if page == "All Complaints":
        st.header("All Complaints")
        complaints = get_complaints()
        for c in complaints:
            with st.expander(f"ID: {c['Complaint_ID']} | Student: {c['Student_Name']} | Type: {c['Problem_Type']} | Status: {c['Status']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**Room:** {c['Room_No']}")
                    st.write(f"**Worker:** {c['Worker_Name'] or 'Unassigned'}")
                    st.write(f"**Warden:** {c['Warden_Name']}")
                    st.write(f"**Date:** {c['Complaint_Date']}")
                    st.write(f"**Description:** {c['Problem_Description']}")
                
                with col2:
                    new_status = st.selectbox(f"Status##status_{c['Complaint_ID']}", ["Pending", "Assigned", "Working in Progress", "Completed"], index=["Pending", "Assigned", "Working in Progress", "Completed"].index(c['Status']))
                    if st.button("Update Status", key=f"update_all_{c['Complaint_ID']}"):
                        con = get_connection(); cur = con.cursor()
                        now = datetime.date.today().isoformat()
                        cur.execute("UPDATE Complaint SET Status = ?, Update_Date = ? WHERE Complaint_ID = ?", (new_status, now, c['Complaint_ID']))
                        con.commit()
                        st.success("Updated!")
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_all_{c['Complaint_ID']}", use_container_width=True):
                        con = get_connection(); cur = con.cursor()
                        cur.execute("DELETE FROM Complaint WHERE Complaint_ID = ?", (c['Complaint_ID'],))
                        con.commit()
                        st.success("Deleted!")
                        st.rerun()
    
    elif page == "Assign/Remove Workers":
        st.header("Manage Worker Assignments")
        con = get_connection(); cur = con.cursor()
        
        # Get all complaints with worker info
        cur.execute("""
SELECT c.*, s.Student_Name, w.Worker_Name FROM Complaint c
JOIN Student s ON c.Student_ID = s.Student_ID
LEFT JOIN Worker w ON c.Worker_ID = w.Worker_ID
ORDER BY c.Complaint_ID
""")
        complaints = cur.fetchall()
        
        tab1, tab2 = st.tabs(["Assign Workers", "Remove Workers"])
        
        with tab1:
            st.subheader("Assign Workers to Complaints")
            complaint_id = st.number_input("Complaint ID", min_value=1, step=1, key="assign_complaint")
            worker_options = {f"{w['Worker_Name']} ({w['Work_Type']})": w['Worker_ID'] for w in get_workers()}
            worker_name = st.selectbox("Select Worker", list(worker_options.keys()), key="assign_worker")
            if st.button("Assign Worker", key="assign_btn"):
                worker_id = worker_options[worker_name]
                con = get_connection(); cur = con.cursor()
                now = datetime.date.today().isoformat()
                cur.execute("UPDATE Complaint SET Worker_ID = ?, Admin_ID = ?, Update_Date = ? WHERE Complaint_ID = ?", (worker_id, user['Admin_ID'], now, complaint_id))
                con.commit()
                st.success(f"Worker '{worker_name}' assigned to Complaint #{complaint_id}")
                st.rerun()
            
            st.divider()
            st.subheader("Current Assignments")
            for c in complaints:
                if c['Worker_Name']:
                    st.info(f"Complaint #{c['Complaint_ID']} | {c['Student_Name']} | **Assigned to:** {c['Worker_Name']}")
                else:
                    st.warning(f"Complaint #{c['Complaint_ID']} | {c['Student_Name']} | **Unassigned**")
        
        with tab2:
            st.subheader("Remove Workers from Complaints")
            complaint_id_remove = st.number_input("Complaint ID", min_value=1, step=1, key="remove_complaint")
            if st.button("Remove Worker", key="remove_btn"):
                con = get_connection(); cur = con.cursor()
                now = datetime.date.today().isoformat()
                cur.execute("UPDATE Complaint SET Worker_ID = NULL, Update_Date = ? WHERE Complaint_ID = ?", (now, complaint_id_remove))
                con.commit()
                st.success(f"Worker removed from Complaint #{complaint_id_remove}")
                st.rerun()
            
            st.divider()
            st.subheader("Current Assignments")
            for c in complaints:
                if c['Worker_Name']:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.info(f"Complaint #{c['Complaint_ID']} | {c['Student_Name']} | **Assigned to:** {c['Worker_Name']}")
                    with col2:
                        if st.button("Remove", key=f"remove_quick_{c['Complaint_ID']}"):
                            con = get_connection(); cur = con.cursor()
                            now = datetime.date.today().isoformat()
                            cur.execute("UPDATE Complaint SET Worker_ID = NULL, Update_Date = ? WHERE Complaint_ID = ?", (now, c['Complaint_ID']))
                            con.commit()
                            st.success(f"Worker removed!")
                            st.rerun()
                else:
                    st.caption(f"Complaint #{c['Complaint_ID']} | {c['Student_Name']} | Unassigned")
    
    elif page == "Reports":
        st.header("Reports & Management")
        con = get_connection(); cur = con.cursor()
        
        # Total complaints
        cur.execute("SELECT COUNT(*) FROM Complaint")
        total = cur.fetchone()[0]
        st.metric("Total Complaints", total)
        
        col1, col2 = st.columns(2)
        
        # By status
        with col1:
            st.subheader("By Status")
            cur.execute("SELECT Status, COUNT(*) as count FROM Complaint GROUP BY Status")
            statuses = cur.fetchall()
            for s in statuses:
                st.write(f"**{s['Status']}**: {s['count']}")
        
        # By worker
        with col2:
            st.subheader("By Worker")
            cur.execute("""
SELECT w.Worker_Name, COUNT(c.Complaint_ID) AS Total_Work
FROM Worker w
LEFT JOIN Complaint c ON w.Worker_ID = c.Worker_ID
GROUP BY w.Worker_Name
""")
            workers = cur.fetchall()
            for w in workers:
                st.write(f"**{w['Worker_Name']}**: {w['Total_Work']}")
        
        st.divider()
        st.subheader("Manage Complaints")
        
        # Get all complaints for editing
        cur.execute("""
SELECT c.*, s.Student_Name FROM Complaint c
JOIN Student s ON c.Student_ID = s.Student_ID
ORDER BY c.Complaint_Date DESC
""")
        complaints = cur.fetchall()
        
        for c in complaints:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**#{c['Complaint_ID']}** - {c['Student_Name']} (Room {c['Room_No']}) | {c['Problem_Type']}")
                st.caption(f"Status: {c['Status']} | Date: {c['Complaint_Date']}")
            
            with col2:
                new_status = st.selectbox(f"##status_{c['Complaint_ID']}", ["Pending", "Assigned", "Working in Progress", "Completed"], index=["Pending", "Assigned", "Working in Progress", "Completed"].index(c['Status']))
                if st.button("Update", key=f"update_report_{c['Complaint_ID']}"):
                    con = get_connection(); cur = con.cursor()
                    now = datetime.date.today().isoformat()
                    cur.execute("UPDATE Complaint SET Status = ?, Update_Date = ? WHERE Complaint_ID = ?", (new_status, now, c['Complaint_ID']))
                    con.commit()
                    st.success("Updated!")
                    st.rerun()
            
            with col3:
                if st.button("Delete", key=f"delete_report_{c['Complaint_ID']}", use_container_width=True):
                    con = get_connection(); cur = con.cursor()
                    cur.execute("DELETE FROM Complaint WHERE Complaint_ID = ?", (c['Complaint_ID'],))
                    con.commit()
                    st.success("Deleted!")
                    st.rerun()
    
    else:
        st.session_state.clear()
        st.rerun()

def main():
    st.title("Hostel Complaint Management System")
    
    if 'user' not in st.session_state:
        role = st.selectbox("Login as", ["Student", "Warden", "Worker", "Admin"])
        if role == "Student":
            option = st.radio("Student access", ["Login", "Register"], horizontal=True)
            if option == "Login":
                student_login()
            else:
                register_student()
        elif role == "Warden":
            warden_login()
        elif role == "Worker":
            worker_login()
        elif role == "Admin":
            admin_login()
    else:
        role = st.session_state['role']
        if role == 'student':
            student_dashboard()
        elif role == 'warden':
            warden_dashboard()
        elif role == 'worker':
            worker_dashboard()
        elif role == 'admin':
            admin_dashboard()

if __name__ == "__main__":
    main()
