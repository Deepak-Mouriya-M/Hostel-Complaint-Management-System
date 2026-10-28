# Hostel Complaint Management System

## Overview
A Python-based Hostel Complaint Management System built with SQLite for backend and Streamlit frontend. Manages complaints from students, handled by wardens, workers, and admins.

## Features
- **Student Module**:
  - Login
  - Submit complaints (problem type, description)
  - View personal complaints
- **Warden Module**:
  - Login
  - View all complaints
  - Update complaint status
- **Worker Module**:
  - Login
  - View assigned complaints
  - Update status of assigned complaints
- **Admin Module**:
  - Login
  - View all complaints
  - Assign workers to complaints
  - Generate reports (total complaints, by status, by worker)

## Database Entities
- Hostel (Hostel_ID, Hostel_Name, Hostel_Type, Floor, Room_No)
- Student (Student_ID, Student_Name, Username, Password, Room_No)
- Warden (Warden_ID, Warden_Name, Warden_Ph_No, Username, Password)
- Worker (Worker_ID, Worker_Name, Worker_Ph_No, Work_Type, Username, Password)
- Admin (Admin_ID, Admin_Name, Username, Password)
- Complaint (Complaint_ID, Room_No, Student_ID, Worker_ID, Warden_ID, Admin_ID, Problem_Type, Problem_Description, Status, Complaint_Date, Update_Date)

## Setup
1. Ensure Python 3.10+ installed.
2. Run `python main.py` to initialize the database with sample data.
3. Run `streamlit run streamlit_app.py` for the GUI.

## Default Credentials
- Student: arun01 / pass01, vijay02 / pass02, etc.
- Warden: warden1 / pass1, etc.
- Worker: worker1 / pass1, etc.
- Admin: admin1 / adminpass, etc.

## Database File
- `hostel_complaints.db` created automatically with sample data.

## Notes
- Statuses: Pending, Assigned, Working in Progress, Completed
- Problem Types: Electric Issue, Water Issue, Furniture Issue, Plumbing Issue, Cleaning Issue, Network Issue
