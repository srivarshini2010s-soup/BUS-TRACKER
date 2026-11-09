import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium

# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="MAV School Bus Tracker",
    page_icon="🚌",
    layout="wide"
)

# ==========================================================
# 2. DATABASE CONNECTION
# ==========================================================
conn = sqlite3.connect("bus_tracker.db", check_same_thread=False)

# ==========================================================
# 3. CUSTOM CSS STYLING
# ==========================================================
st.markdown("""
<style>
.main {
    background-color: #0B2920;
}
.stSidebar {
    background-color: #0F382E;
}
div.stButton > button:first-child {
    background-color: #1A7A5E;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}
div.stButton > button:hover {
    background-color: #249673;
    color: white;
}
.card {
    background: #0F382E;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
hr {
    border-color: #1A4A3C;
}
.stRadio label {
    color: #F5F5F3 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 4. CREDENTIALS (40 Parents + Admin)
# ==========================================================
def _h(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

USERS = {
    "admin": {"password": _h("Admin@2015"), "role": "admin"},
    # Multi-child parents
    "vijay.sethupathi":   {"password": _h("Vijay@2017"),   "role": "parent"},
    "nayanthara.nair":    {"password": _h("Nayan@2018"),    "role": "parent"},
    "suriya.sivakumar":   {"password": _h("Suriya@2016"),   "role": "parent"},
    "keerthy.suresh":     {"password": _h("Keerthy@2019"), "role": "parent"},
    "dhanush.r":          {"password": _h("Dhanush@2017"), "role": "parent"},
    "sai.pallavi":        {"password": _h("Sai@2020"),      "role": "parent"},
    "sivakarthikeyan.s":  {"password": _h("SK@2018"),       "role": "parent"},
    "trisha.krishnan":    {"password": _h("Trisha@2015"),   "role": "parent"},
    "karthi.sivakumar":   {"password": _h("Karthi@2019"),   "role": "parent"},
    # Single-child parents
    "aishwarya.rajesh":   {"password": _h("Aishwarya@2021"), "role": "parent"},
    "jayam.ravi":         {"password": _h("Jayam@2016"),     "role": "parent"},
    "samantha.ruth":      {"password": _h("Samantha@2017"),  "role": "parent"},
    "vikram.prabhu":      {"password": _h("Vikram@2020"),    "role": "parent"},
    "raashi.khanna":      {"password": _h("Raashi@2022"),    "role": "parent"},
    "arya.t":             {"password": _h("Arya@2018"),      "role": "parent"},
    "pooja.hegde":        {"password": _h("Pooja@2021"),     "role": "parent"},
    "simbu.t":            {"password": _h("Simbu@2015"),     "role": "parent"},
    "kalyani.priyadarshan":{"password": _h("Kalyani@2023"),  "role": "parent"},
    "madhavan.r":         {"password": _h("Maddy@2014"),     "role": "parent"},
    "nivetha.thomas":     {"password": _h("Nivetha@2019"),   "role": "parent"},
    "vishal.krishna":     {"password": _h("Vishal@2016"),    "role": "parent"},
    "amala.paul":         {"password": _h("Amala@2020"),     "role": "parent"},
    "atharvaa.murali":    {"password": _h("Atharvaa@2022"),  "role": "parent"},
    "priya.bhavani":      {"password": _h("Priya@2021"),     "role": "parent"},
    "gv.prakash":         {"password": _h("GV@2017"),        "role": "parent"},
    "anandhi.s":          {"password": _h("Anandhi@2018"),   "role": "parent"},
    "hiphop.tamizha":     {"password": _h("Hiphop@2019"),    "role": "parent"},
    "bindu.madhavi":      {"password": _h("Bindu@2020"),     "role": "parent"},
    "sundeep.kishan":     {"password": _h("Sundeep@2022"),   "role": "parent"},
    "regina.cassandra":   {"password": _h("Regina@2016"),    "role": "parent"},
    "harish.kalyan":      {"password": _h("Harish@2021"),    "role": "parent"},
    "raiza.wilson":       {"password": _h("Raiza@2023"),     "role": "parent"},
    "ashok.selvan":       {"password": _h("Ashok@2018"),     "role": "parent"},
    "andrea.jeremiah":    {"password": _h("Andrea@2015"),    "role": "parent"},
    "bobby.simha":        {"password": _h("Bobby@2017"),     "role": "parent"},
    "tanya.ravichandran": {"password": _h("Tanya@2020"),     "role": "parent"},
    "rj.balaji":          {"password": _h("RJ@2019"),        "role": "parent"},
    "nithya.menen":       {"password": _h("Nithya@2016"),    "role": "parent"},
    "siddharth.s":        {"password": _h("Sid@2014"),       "role": "parent"},
    "amal.paul":          {"password": _h("Amal@2022"),      "role": "parent"},
}

# ==========================================================
# 5. SESSION STATE
# ==========================================================
defaults = {
    "logged_in": False,
    "role": None,
    "username": None,
    "parent_student": None,
    "eta_by_bus": {}
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================================
# 6. DATABASE TABLES SETUP & SEEDING
# ==========================================================
def table_columns(table_name):
    """Return the column names for a SQLite table."""
    try:
        return [
            row[1]
            for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        ]
    except Exception:
        return []

def ensure_table_type_and_columns(table_name, expected_columns, create_sql):
    """Ensure that an object with this name is a table with the expected schema."""
    object_row = conn.execute(
        "SELECT type FROM sqlite_master WHERE name = ?", (table_name,)
    ).fetchone()

    if object_row and object_row[0] != "table":
        conn.execute(f'DROP VIEW IF EXISTS "{table_name}"')
        conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')

    existing_columns = table_columns(table_name)
    if existing_columns and existing_columns != expected_columns:
        conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')

    conn.execute(create_sql)
    conn.commit()

# Create tables
ensure_table_type_and_columns(
    "buses",
    ["bus_no", "driver", "route_no", "route_name", "latitude", "longitude", "speed", "status"],
    """
    CREATE TABLE IF NOT EXISTS buses (
        bus_no TEXT PRIMARY KEY,
        driver TEXT NOT NULL,
        route_no TEXT NOT NULL,
        route_name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        speed INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'Stopped'
    )
    """
)

ensure_table_type_and_columns(
    "students",
    ["admission_no", "student_name", "bus_no", "pickup_point", "parent_username", "grade"],
    """
    CREATE TABLE IF NOT EXISTS students (
        admission_no TEXT PRIMARY KEY,
        student_name TEXT NOT NULL,
        bus_no TEXT NOT NULL,
        pickup_point TEXT NOT NULL,
        parent_username TEXT NOT NULL,
        grade TEXT NOT NULL
    )
    """
)

ensure_table_type_and_columns(
    "leave_requests",
    ["leave_id", "admission_no", "student_name", "bus_no", "leave_date", "reason", "parent_username", "status"],
    """
    CREATE TABLE IF NOT EXISTS leave_requests (
        leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
        admission_no TEXT NOT NULL,
        student_name TEXT NOT NULL,
        bus_no TEXT NOT NULL,
        leave_date TEXT NOT NULL,
        reason TEXT NOT NULL,
        parent_username TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending'
    )
    """
)

ensure_table_type_and_columns(
    "route_reports",
    ["report_id", "bus_no", "report_date", "issue_type", "description", "status"],
    """
    CREATE TABLE IF NOT EXISTS route_reports (
        report_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bus_no TEXT NOT NULL,
        report_date TEXT NOT NULL,
        issue_type TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Open'
    )
    """
)

# Seed initial data if empty
def seed_database():
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM buses")
    if cursor.fetchone()[0] == 0:
        sample_buses = [
            ("BUS-01", "Murugan", "R-101", "Tambaram to School", 12.9249, 80.1499, 35, "Running"),
            ("BUS-02", "Selvam", "R-102", "Adyar to School", 13.0012, 80.2565, 0, "Stopped"),
            ("BUS-03", "Karthik", "R-103", "Velachery to School", 12.9810, 80.2206, 42, "Running"),
            ("BUS-04", "Ramesh", "R-104", "T Nagar to School", 13.0418, 80.2341, 28, "Running")
        ]
        cursor.executemany("INSERT INTO buses VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_buses)

    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ("ADM-101", "Aarav Sethupathi", "BUS-01", "Camp Road Junction", "vijay.sethupathi", "5th Std"),
            ("ADM-102", "Ananya Sethupathi", "BUS-01", "Chromepet Signal", "vijay.sethupathi", "3rd Std"),
            ("ADM-103", "Diya Nair", "BUS-02", "Kasturba Nagar", "nayanthara.nair", "4th Std"),
            ("ADM-104", "Kabir Sivakumar", "BUS-03", "Vijayanagar", "suriya.sivakumar", "6th Std"),
            ("ADM-105", "Meera Suresh", "BUS-04", "Panagal Park", "keerthy.suresh", "2nd Std")
        ]
        cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", sample_students)
        conn.commit()

seed_database()

# ==========================================================
# 7. AUTHENTICATION & PORTALS
# ==========================================================
st.sidebar.title("🚌 MAV School Bus Tracker")

if not st.session_state["logged_in"]:
    st.sidebar.subheader("Login Portal")
    username = st.sidebar.text_input("Username").strip().lower()
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username in USERS and USERS[username]["password"] == _h(password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = USERS[username]["role"]
            st.rerun()
        else:
            st.sidebar.error("Invalid Username or Password")
else:
    st.sidebar.success(f"Logged in as: {st.session_state['username']}")
    if st.sidebar.button("Logout"):
        for key in defaults:
            st.session_state[key] = defaults[key]
        st.rerun()

    # --- ADMIN PORTAL ---
    if st.session_state["role"] == "admin":
        st.title("🛡️ Admin Dashboard - MAV Bus Tracker")
        
        tab1, tab2, tab3 = st.tabs(["Manage Buses", "Student Records", "Live Fleet Map"])
        
        with tab1:
            st.subheader("Bus Fleet Status")
            buses_df = pd.read_sql("SELECT * FROM buses", conn)
            st.dataframe(buses_df, use_container_width=True)
            
            with st.form("add_bus_form"):
                st.subheader("Add / Update Bus")
                b_no = st.text_input("Bus Number (e.g., BUS-05)")
                driver = st.text_input("Driver Name")
                r_no = st.text_input("Route Number")
                r_name = st.text_input("Route Name")
                lat = st.number_input("Latitude", value=13.0827, format="%.4f")
                lon = st.number_input("Longitude", value=80.2707, format="%.4f")
                speed = st.number_input("Speed (km/h)", value=0, step=1)
                status = st.selectbox("Status", ["Running", "Stopped", "Maintenance"])
                
                if st.form_submit_button("Save Bus"):
                    if b_no:
                        conn.execute("""
                            INSERT INTO buses (bus_no, driver, route_no, route_name, latitude, longitude, speed, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(bus_no) DO UPDATE SET
                            driver=excluded.driver, route_no=excluded.route_no, route_name=excluded.route_name,
                            latitude=excluded.latitude, longitude=excluded.longitude, speed=excluded.speed, status=excluded.status
                        """, (b_no, driver, r_no, r_name, lat, lon, speed, status))
                        conn.commit()
                        st.success(f"Bus {b_no} saved successfully!")
                        st.rerun()
                    else:
                        st.error("Bus Number is required.")

        with tab2:
            st.subheader("Enrolled Students")
            students_df = pd.read_sql("SELECT * FROM students", conn)
            st.dataframe(students_df, use_container_width=True)

        with tab3:
            st.subheader("Live Fleet Tracking Map")
            buses_df = pd.read_sql("SELECT * FROM buses", conn)
            m = folium.Map(location=[13.02, 80.22], zoom_index=12)
            for _, row in buses_df.iterrows():
                folium.Marker(
                    [row["latitude"], row["longitude"]],
                    popup=f"<b>{row['bus_no']}</b><br>Driver: {row['driver']}<br>Status: {row['status']}",
                    icon=folium.Icon(color="green" if row["status"] == "Running" else "red", icon="bus", prefix="fa")
                ).add_to(m)
            st_folium(m, width=700, height=500)

    # --- PARENT PORTAL ---
    elif st.session_state["role"] == "parent":
        parent_user = st.session_state["username"]
        st.title(f"👨‍👩‍👧 Parent Portal - Welcome, {parent_user.title()}")
        
        children_df = pd.read_sql("SELECT * FROM students WHERE parent_username = ?", conn, params=(parent_user,))
        
        if children_df.empty:
            st.warning("No children records found linked to this account.")
        else:
            tabs = st.tabs([f"Child: {row['student_name']}" for _, row in children_df.iterrows()])
            
            for idx, (_, child) in enumerate(children_df.iterrows()):
                with tabs[idx]:
                    st.markdown(f"### Student Details: {child['student_name']}")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Admission No:** {child['admission_no']}")
                        st.write(f"**Grade:** {child['grade']}")
                        st.write(f"**Assigned Bus:** {child['bus_no']}")
                        st.write(f"**Pickup Point:** {child['pickup_point']}")
                    
                    with col2:
                        bus_info = pd.read_sql("SELECT * FROM buses WHERE bus_no = ?", conn, params=(child['bus_no'],)).iloc[0]
                        st.write(f"**Driver:** {bus_info['driver']}")
                        st.write(f"**Route:** {bus_info['route_name']} ({bus_info['route_no']})")
                        st.write(f"**Bus Status:** {bus_info['status']}")
                        st.write(f"**Current Speed:** {bus_info['speed']} km/h")

                    st.markdown("---")
                    st.subheader("Live Bus Location")
                    m_parent = folium.Map(location=[bus_info['latitude'], bus_info['longitude']], zoom=14)
                    folium.Marker(
                        [bus_info['latitude'], bus_info['longitude']],
                        popup=f"Bus {bus_info['bus_no']} - {bus_info['status']}",
                        icon=folium.Icon(color="blue", icon="bus", prefix="fa")
                    ).add_to(m_parent)
                    st_folium(m_parent, width=650, height=400)

                    st.markdown("---")
                    st.subheader("Apply for Student Leave")
                    with st.form(f"leave_form_{child['admission_no']}"):
                        leave_date = st.date_input("Leave Date")
                        reason = st.text_area("Reason for Leave")
                        if st.form_submit_button("Submit Leave Request"):
                            conn.execute("""
                                INSERT INTO leave_requests (admission_no, student_name, bus_no, leave_date, reason, parent_username, status)
                                VALUES (?, ?, ?, ?, ?, ?, 'Pending')
                            """, (child['admission_no'], child['student_name'], child['bus_no'], str(leave_date), reason, parent_user))
                            conn.commit()
                            st.success("Leave request submitted successfully!")
