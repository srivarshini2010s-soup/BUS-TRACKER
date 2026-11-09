import streamlit as st
import pandas as pd
import sqlite3
import folium
import random
import hashlib
from pathlib import Path
from datetime import date
from streamlit_folium import st_folium

# ==========================================================
# 1. PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="MAV School Bus Tracker",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# 2. DATABASE
# ==========================================================
DB_PATH = Path(__file__).resolve().parent / "bus_tracking.db"
conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)

# ==========================================================
# 3. DARK LUXURY THEME (WITH MOBILE WEBKIT OVERRIDES)
# ==========================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* Global Dark Theme */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background-color: #0B1312 !important;
    color: #F5F5F3 !important;
}
[data-testid="stHeader"] {
    background: #0B1312 !important;
}
h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    color: #F5F5F3 !important;
    letter-spacing: 0.3px;
}
p, label, span, li, .stMarkdown, .stCaption {
    color: #F5F5F3 !important;
}

/* Sidebar Fixes for Mobile */
section[data-testid="stSidebar"] {
    background-color: #0F382E !important;
}
section[data-testid="stSidebar"] * {
    color: #F5F5F3 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: #D4AF37 !important;
    color: #0B1312 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    border: none !important;
}

/* Metrics Fixes */
div[data-testid="stMetric"] {
    background: #0F382E !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 14px !important;
    padding: 16px !important;
}
div[data-testid="stMetric"] label {
    color: #D4AF37 !important;
    font-weight: 600 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #F5F5F3 !important;
    font-weight: 700 !important;
}

/* Button Fixes */
.stButton > button,
.stFormSubmitButton > button {
    background: #D4AF37 !important;
    color: #0B1312 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #E8C547 !important;
    color: #0B1312 !important;
}

/* Mobile Input, Textarea, and Select Overrides */
input, textarea, select, 
.stTextInput input, 
.stTextArea textarea,
.stDateInput input,
[data-baseweb="input"] input {
    background-color: #0F382E !important;
    color: #F5F5F3 !important;
    -webkit-text-fill-color: #F5F5F3 !important;
    border-radius: 10px !important;
    border: 1px solid #D4AF37 !important;
    opacity: 1 !important;
}

/* Placeholders Visibility Fix */
::placeholder,
::-webkit-input-placeholder {
    color: #A0B2AC !important;
    -webkit-text-fill-color: #A0B2AC !important;
    opacity: 1 !important;
}

/* Password Eye Icon & Native SVG Controls Fix */
button[aria-label="Show password"],
button[aria-label="Hide password"],
svg[data-icon="eye"],
svg[data-icon="eye-slash"] {
    fill: #D4AF37 !important;
    color: #D4AF37 !important;
    filter: drop-shadow(0 0 1px #D4AF37);
}

/* Selectbox Dropdown Fixes for Mobile */
div[data-baseweb="select"] {
    background-color: #0F382E !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] > div {
    background-color: #0F382E !important;
    color: #F5F5F3 !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] * {
    color: #F5F5F3 !important;
    -webkit-text-fill-color: #F5F5F3 !important;
}
ul[data-baseweb="menu"] {
    background-color: #0F382E !important;
    border: 1px solid #D4AF37 !important;
}
ul[data-baseweb="menu"] li,
ul[data-baseweb="menu"] li * {
    background-color: #0F382E !important;
    color: #F5F5F3 !important;
    -webkit-text-fill-color: #F5F5F3 !important;
}
ul[data-baseweb="menu"] li:hover {
    background-color: #1A4A3C !important;
}

/* Labels Fix */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stDateInput"] label {
    color: #D4AF37 !important;
    font-weight: 600 !important;
}

/* Mobile Alert Cards (st.info, st.warning, st.error, st.success) */
div[data-testid="stAlert"] {
    background-color: #0F382E !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 12px !important;
    color: #F5F5F3 !important;
}
div[data-testid="stAlert"] * {
    color: #F5F5F3 !important;
    -webkit-text-fill-color: #F5F5F3 !important;
}

/* Expander Header & Content Mobile Overrides */
div[data-testid="stExpander"] {
    background-color: #0F382E !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 12px !important;
}
div[data-testid="stExpander"] * {
    color: #F5F5F3 !important;
    -webkit-text-fill-color: #F5F5F3 !important;
}

/* Card & Login Layout */
.login-card {
    background: #0F382E !important;
    border-radius: 20px;
    padding: 30px 24px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.55);
    border: 1.5px solid #D4AF37;
    max-width: 420px;
    margin: 0 auto;
}
.main-title {
    font-family: 'Playfair Display', serif !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
    color: #D4AF37 !important;
    text-align: center;
    margin-bottom: 6px;
}
.subtitle {
    text-align: center;
    color: #F5F5F3 !important;
    font-weight: 500 !important;
    font-size: 0.95rem;
    margin-bottom: 24px;
    opacity: 0.9;
}
[data-testid="stDataFrame"] {
    background: #0F382E !important;
    border-radius: 12px;
}
hr {
    border-color: #1A4A3C !important;
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
    "vijay.sethupathi":   {"password": _h("Vijay@2017"),   "role": "parent"},
    "nayanthara.nair":    {"password": _h("Nayan@2018"),    "role": "parent"},
    "suriya.sivakumar":   {"password": _h("Suriya@2016"),   "role": "parent"},
    "keerthy.suresh":     {"password": _h("Keerthy@2019"), "role": "parent"},
    "dhanush.r":          {"password": _h("Dhanush@2017"), "role": "parent"},
    "sai.pallavi":        {"password": _h("Sai@2020"),      "role": "parent"},
    "sivakarthikeyan.s":  {"password": _h("SK@2018"),       "role": "parent"},
    "trisha.krishnan":    {"password": _h("Trisha@2015"),   "role": "parent"},
    "karthi.sivakumar":   {"password": _h("Karthi@2019"),   "role": "parent"},
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
# 6. DATABASE TABLES SETUP
# ==========================================================
try:
    b_cols = [r[1] for r in conn.execute("PRAGMA table_info(buses)").fetchall()]
    if len(b_cols) > 0 and len(b_cols) != 8:
        conn.execute("DROP TABLE buses")
        conn.commit()
except Exception:
    pass

conn.execute("""
CREATE TABLE IF NOT EXISTS buses (
    bus_no TEXT PRIMARY KEY,
    driver TEXT,
    route_no TEXT,
    route_name TEXT,
    latitude REAL,
    longitude REAL,
    speed INTEGER,
    status TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS students (
    admission_no TEXT PRIMARY KEY,
    student_name TEXT,
    bus_no TEXT,
    pickup_point TEXT,
    parent_username TEXT,
    grade TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS leave_requests (
    leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT,
    student_name TEXT,
    bus_no TEXT,
    leave_date TEXT,
    reason TEXT,
    parent_username TEXT,
    status TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS route_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT,
    student_name TEXT,
    bus_no TEXT,
    description TEXT,
    parent_username TEXT,
    report_status TEXT
)
""")
conn.commit()

# ==========================================================
# 7. SEED DATA
# ==========================================================
def seed_data():
    buses = [
        ("TN09AB1001", "Murugan S",     "R-01", "Kaithi Route",        12.9249, 80.1000, 32, "Moving"),
        ("TN09CD1002", "Selvam K",      "R-02", "Vikram Trail",        12.9516, 80.1462, 28, "Moving"),
        ("TN09EF1003", "Ravi Chandran", "R-03", "Master Path",         12.9675, 80.1491,  0, "Stopped"),
        ("TN09GH1004", "Anand Babu",    "R-04", "Beast Circuit",       12.9172, 80.1320, 35, "Moving"),
        ("TN09IJ1005", "Karthikeyan M", "R-05", "Jailer Expressway",   12.9200, 80.1900, 30, "Moving"),
        ("TN09KL1006", "Senthil Kumar", "R-06", "Leo Route",           12.9000, 80.2270, 22, "Moving"),
        ("TN09MN1007", "Prabhu D",      "R-07", "Soorarai Pottru",     12.9750, 80.2200,  0, "Stopped"),
        ("TN09OP1008", "Ganesh R",      "R-08", "Vettaiya Boulevard",  13.0100, 80.2100, 27, "Moving"),
        ("TN09QR1009", "Vignesh P",     "R-09", "Thalapathy Line",     13.0060, 80.2570, 25, "Moving"),
        ("TN09ST1010", "Muthuvel A",    "R-10", "Thanga Magan Way",    13.0400, 80.2340, 18, "Moving"),
        ("TN09UV1011", "Suresh Babu",   "R-11", "Ponniyin Selvan",     13.0850, 80.2100,  0, "Stopped"),
        ("TN09WX1012", "Balaji N",      "R-12", "Indian 2 Link",       13.0380, 80.1560, 33, "Moving"),
    ]
    for b in buses:
        conn.execute("INSERT OR IGNORE INTO buses VALUES (?,?,?,?,?,?,?,?)", b)

    students = [
        ("1001", "Aadhya Sethupathi",  "TN09AB1001", "Tambaram",        "vijay.sethupathi", "Class 5"),
        ("1002", "Kavin Sethupathi",   "TN09AB1001", "Tambaram",        "vijay.sethupathi", "Class 3"),
        ("1003", "Nila Sethupathi",    "TN09CD1002", "Chromepet",       "vijay.sethupathi", "Class 1"),
        ("1004", "Arjun Nair",         "TN09EF1003", "Pallavaram",      "nayanthara.nair",  "Class 7"),
        ("1005", "Meera Nair",         "TN09EF1003", "Pallavaram",      "nayanthara.nair",  "Class 4"),
        ("1006", "Vihaan Sivakumar",   "TN09GH1004", "Selaiyur",        "suriya.sivakumar", "Class 8"),
        ("1007", "Ananya Sivakumar",   "TN09GH1004", "Selaiyur",        "suriya.sivakumar", "Class 6"),
        ("1008", "Rohan Suresh",       "TN09IJ1005", "Medavakkam",      "keerthy.suresh",   "Class 9"),
        ("1009", "Ishaan Suresh",      "TN09IJ1005", "Medavakkam",      "keerthy.suresh",   "Class 5"),
        ("1010", "Diya Dhanush",       "TN09KL1006", "Sholinganallur",  "dhanush.r",        "Class 2"),
        ("1011", "Kabir Dhanush",      "TN09KL1006", "Sholinganallur",  "dhanush.r",        "Class 6"),
        ("1012", "Saanvi Pallavi",     "TN09MN1007", "Velachery",       "sai.pallavi",      "Class 10"),
        ("1013", "Aryan Pallavi",      "TN09MN1007", "Velachery",       "sai.pallavi",      "Class 7"),
        ("1014", "Myra Karthikeyan",   "TN09OP1008", "Guindy",          "sivakarthikeyan.s","Class 3"),
        ("1015", "Vivaan Karthikeyan", "TN09OP1008", "Guindy",          "sivakarthikeyan.s","Class 1"),
        ("1016", "Aisha Krishnan",     "TN09QR1009", "Adyar",           "trisha.krishnan",  "Class 11"),
        ("1017", "Reyansh Krishnan",   "TN09QR1009", "Adyar",           "trisha.krishnan",  "Class 8"),
        ("1018", "Pari Karthi",        "TN09ST1010", "T Nagar",         "karthi.sivakumar", "Class 4"),
        ("1019", "Advait Karthi",      "TN09ST1010", "T Nagar",         "karthi.sivakumar", "Class 2"),
        ("1020", "Kiara Rajesh",       "TN09UV1011", "Anna Nagar",      "aishwarya.rajesh", "Class 6"),
        ("1021", "Shaurya Ravi",       "TN09WX1012", "Porur",           "jayam.ravi",       "Class 9"),
        ("1022", "Anvi Ruth",          "TN09AB1001", "Tambaram",        "samantha.ruth",    "Class 5"),
        ("1023", "Dhruv Prabhu",       "TN09CD1002", "Chromepet",       "vikram.prabhu",    "Class 12"),
        ("1024", "Navya Khanna",       "TN09EF1003", "Pallavaram",      "raashi.khanna",    "Class 3"),
        ("1025", "Atharv Arya",        "TN09GH1004", "Selaiyur",        "arya.t",           "Class 7"),
        ("1026", "Sara Hegde",         "TN09IJ1005", "Medavakkam",      "pooja.hegde",      "Class 10"),
        ("1027", "Yuvan TR",           "TN09KL1006", "Sholinganallur",  "simbu.t",          "Class 4"),
        ("1028", "Riya Priyadarshan",  "TN09MN1007", "Velachery",       "kalyani.priyadarshan", "Class 1"),
        ("1029", "Krish Madhavan",     "TN09OP1008", "Guindy",          "madhavan.r",       "Class 8"),
        ("1030", "Zara Thomas",        "TN09QR1009", "Adyar",           "nivetha.thomas",   "Class 6"),
        ("1031", "Aarav Krishna",      "TN09ST1010", "T Nagar",         "vishal.krishna",   "Class 11"),
        ("1032", "Mishka Paul",        "TN09UV1011", "Anna Nagar",      "amala.paul",       "Class 2"),
        ("1033", "Veer Murali",        "TN09WX1012", "Porur",           "atharvaa.murali",  "Class 5"),
        ("1034", "Tara Bhavani",       "TN09AB1001", "Tambaram",        "priya.bhavani",    "Class 9"),
        ("1035", "Om Prakash",         "TN09CD1002", "Chromepet",       "gv.prakash",       "Class 3"),
        ("1036", "Ira Anandhi",        "TN09EF1003", "Pallavaram",      "anandhi.s",        "Class 7"),
        ("1037", "Laksh Tamizha",      "TN09GH1004", "Selaiyur",        "hiphop.tamizha",   "Class 12"),
        ("1038", "Sia Madhavi",        "TN09IJ1005", "Medavakkam",      "bindu.madhavi",    "Class 4"),
        ("1039", "Neil Kishan",        "TN09KL1006", "Sholinganallur",  "sundeep.kishan",   "Class 8"),
        ("1040", "Aanya Cassandra",    "TN09MN1007", "Velachery",       "regina.cassandra", "Class 6"),
        ("1041", "Rudra Kalyan",       "TN09OP1008", "Guindy",          "harish.kalyan",    "Class 10"),
        ("1042", "Kyra Wilson",        "TN09QR1009", "Adyar",           "raiza.wilson",     "Class 2"),
        ("1043", "Dev Selvan",         "TN09ST1010", "T Nagar",         "ashok.selvan",     "Class 5"),
        ("1044", "Lila Jeremiah",      "TN09UV1011", "Anna Nagar",      "andrea.jeremiah",  "Class 1"),
        ("1045", "Yash Simha",         "TN09WX1012", "Porur",           "bobby.simha",      "Class 9"),
        ("1046", "Nina Ravichandran",  "TN09AB1001", "Tambaram",        "tanya.ravichandran","Class 3"),
        ("1047", "Sam Balaji",         "TN09CD1002", "Chromepet",       "rj.balaji",        "Class 7"),
        ("1048", "Eva Menen",          "TN09EF1003", "Pallavaram",      "nithya.menen",     "Class 11"),
        ("1049", "Jai Siddharth",      "TN09GH1004", "Selaiyur",        "siddharth.s",      "Class 4"),
        ("1050", "Maya Amal",          "TN09IJ1005", "Medavakkam",      "amal.paul",        "Class 8"),
    ]
    for s in students:
        conn.execute("INSERT OR IGNORE INTO students VALUES (?,?,?,?,?,?)", s)
    conn.commit()

seed_data()

# ==========================================================
# 8. HELPERS
# ==========================================================
def get_buses():
    return pd.read_sql_query(
        "SELECT bus_no, driver, route_no, route_name, latitude, longitude, speed, status FROM buses ORDER BY bus_no",
        conn
    )

def get_students():
    return pd.read_sql_query(
        "SELECT admission_no, student_name, bus_no, pickup_point, parent_username, grade FROM students ORDER BY admission_no",
        conn
    )

def get_bus_details(bus_number):
    return conn.execute(
        "SELECT bus_no, driver, route_no, route_name, latitude, longitude, speed, status FROM buses WHERE bus_no = ?",
        (bus_number,)
    ).fetchone()

def get_children_of_parent(username):
    return pd.read_sql_query("""
        SELECT admission_no, student_name, bus_no, pickup_point, grade
        FROM students
        WHERE LOWER(parent_username) = ?
        ORDER BY admission_no
    """, conn, params=(username.lower(),))

# ==========================================================
# 9. LOGIN PAGE
# ==========================================================
if not st.session_state.logged_in:
    left, center, right = st.columns([1, 8, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="main-title">MAV School Bus Tracker</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Secure School Transportation Portal</div>', unsafe_allow_html=True)
        login_type = st.radio(
            "Portal",
            ["Parent Login", "Admin Login"],
            horizontal=True,
            label_visibility="collapsed"
        )
        username = st.text_input("Username", placeholder="e.g. vijay.sethupathi")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.button("Sign In", use_container_width=True):
            username = username.strip().lower()
            user = USERS.get(username)
            password_hash = _h(password)
            if user and user["password"] == password_hash:
                correct_role = (
                    (login_type == "Parent Login" and user["role"] == "parent")
                    or
                    (login_type == "Admin Login" and user["role"] == "admin")
                )
                if correct_role:
                    st.session_state.logged_in = True
                    st.session_state.role = user["role"]
                    st.session_state.username = username
                    st.session_state.parent_student = None
                    st.rerun()
                else:
                    st.error("Please choose the correct portal for this account.")
            else:
                st.error("Invalid username or password.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================================
# 10. SIDEBAR
# ==========================================================
st.sidebar.markdown("### MAV Tracker")
st.sidebar.write(f"**{st.session_state.username}**")
st.sidebar.write(f"Role: {st.session_state.role.upper()}")
st.sidebar.divider()
if st.sidebar.button("Logout", use_container_width=True):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# ==========================================================
# 11. PARENT PORTAL
# ==========================================================
if st.session_state.role == "parent":
    st.title("Parent Portal")
    st.caption("You can view and manage your linked children.")
    children_df = get_children_of_parent(st.session_state.username)
    if children_df.empty:
        st.warning("No students are linked to this parent account.")
        st.stop()
    
    # Cleaned label formatting to prevent truncation on mobile screen width
    options = [
        f"{row['student_name']} ({row['admission_no']} - {row['grade']})"
        for _, row in children_df.iterrows()
    ]
    choice = st.selectbox("Select your child", options)
    selected_adm = choice.split("(")[1].split(" -")[0].strip()
    student_row = children_df[children_df["admission_no"] == selected_adm].iloc[0]
    admission     = student_row["admission_no"]
    student_name  = student_row["student_name"]
    bus_number    = student_row["bus_no"]
    pickup_point  = student_row["pickup_point"]
    grade         = student_row["grade"]
    
    bus = get_bus_details(bus_number)
    if not bus:
        st.error("Assigned bus information is currently unavailable.")
        st.stop()
    bus_no, driver, route_no, route_name, lat, lon, speed, status = bus
    st.divider()
    st.subheader("Student Information")
    c1, c2, c3 = st.columns(3)
    c1.metric("Student Name", student_name)
    c2.metric("Admission No", admission)
    c3.metric("Grade", grade)
    st.info(f"Pickup Point: **{pickup_point}**")
    st.divider()
    st.subheader("Assigned Bus")
    c1, c2 = st.columns(2)
    c1.metric("Bus Number", bus_no)
    c2.metric("Status", status)
    c3, c4 = st.columns(2)
    c3.metric("Driver", driver)
    c4.metric("Speed", f"{speed} km/h")
    st.write(f"**Route:** {route_no} – {route_name}")
    
    if bus_no not in st.session_state.eta_by_bus:
        st.session_state.eta_by_bus[bus_no] = random.randint(5, 20)
    eta = st.session_state.eta_by_bus[bus_no]
    st.info(f"Estimated Arrival: **{eta} minutes**")
    
    # Map
    st.subheader("Bus Location")
    m = folium.Map(location=[lat, lon], zoom_start=14, tiles="OpenStreetMap")
    folium.Marker(
        [lat, lon],
        popup=f"Bus: {bus_no}",
        tooltip="Your child's bus",
        icon=folium.Icon(color="green" if status == "Moving" else "red", icon="bus", prefix="fa")
    ).add_to(m)
    st_folium(m, width=None, height=420, key="parent_bus_map")
    
    # Wrong Route Report
    st.markdown("---")
    with st.expander("Report Wrong Route", expanded=False):
        st.warning("Use this only if you notice a possible route problem.")
        with st.form("wrong_route_form"):
            route_description = st.text_area(
                "Describe the issue",
                placeholder="Example: The bus is taking a different road than usual.",
                height=110
            )
            report_submit = st.form_submit_button("Submit Report", use_container_width=True)
        if report_submit:
            if not route_description.strip():
                st.warning("Please describe the issue.")
            else:
                conn.execute("""
                    INSERT INTO route_reports
                    (admission_no, student_name, bus_no, description, parent_username, report_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (admission, student_name, bus_no, route_description.strip(),
                      st.session_state.username, "New"))
                conn.commit()
                st.success("Route report submitted successfully.")
                
    # Leave Application
    st.divider()
    st.subheader("Bus Leave Application")
    with st.form("bus_leave_form"):
        leave_date = st.date_input("Leave Date", min_value=date.today())
        leave_reason = st.selectbox(
            "Reason",
            ["Student is absent", "Parent will drop/pick up", "Personal reason", "Sick Leave", "Other"]
        )
        additional_reason = st.text_area("Additional details (optional)")
        st.markdown("**Parent verification**")
        st.caption("Re-enter your account password to confirm this request.")
        verify_password = st.text_input("Re-enter password", type="password", key="leave_pwd")
        leave_submit = st.form_submit_button("Submit Leave", use_container_width=True)
        
    if leave_submit:
        expected = USERS.get(st.session_state.username, {}).get("password")
        if not verify_password or _h(verify_password) != expected:
            st.error("Password verification failed.")
        else:
            final_reason = leave_reason
            if additional_reason.strip():
                final_reason += " – " + additional_reason.strip()
            exists = conn.execute("""
                SELECT COUNT(*) FROM leave_requests
                WHERE admission_no = ? AND leave_date = ?
            """, (admission, leave_date.isoformat())).fetchone()[0]
            if exists:
                st.warning("A leave request already exists for this date.")
            else:
                conn.execute("""
                    INSERT INTO leave_requests
                    (admission_no, student_name, bus_no, leave_date, reason, parent_username, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (admission, student_name, bus_no, leave_date.isoformat(),
                      final_reason, st.session_state.username, "Pending"))
                conn.commit()
                st.success("Leave application submitted.")
                
    # Leave History
    st.divider()
    st.subheader("Your Leave History")
    leave_history = pd.read_sql_query("""
        SELECT leave_date, reason, status
        FROM leave_requests
        WHERE admission_no = ?
        ORDER BY leave_date DESC
    """, conn, params=(admission,))
    if not leave_history.empty:
        st.dataframe(leave_history, use_container_width=True, hide_index=True)
    else:
        st.info("No leave applications yet.")

# ==========================================================
# 12. ADMIN PORTAL
# ==========================================================
elif st.session_state.role == "admin":
    st.title("Admin Dashboard")
    st.caption("MAV School Transportation Management")
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Track Bus", "Bus Management", "Student Management", "Notifications"]
    )
    df = get_buses()
    
    # ---------- DASHBOARD ----------
    if page == "Dashboard":
        st.subheader("Fleet Overview")
        total_buses = len(df)
        moving = len(df[df["status"] == "Moving"]) if not df.empty else 0
        stopped = len(df[df["status"] == "Stopped"]) if not df.empty else 0
        pending_leaves = conn.execute(
            "SELECT COUNT(*) FROM leave_requests WHERE status = 'Pending'"
        ).fetchone()[0]
        new_reports = conn.execute(
            "SELECT COUNT(*) FROM route_reports WHERE report_status = 'New'"
        ).fetchone()[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Buses", total_buses)
        c2.metric("Moving", moving)
        c3.metric("Stopped", stopped)
        
        c4, c5 = st.columns(2)
        c4.metric("Pending Leaves", pending_leaves)
        c5.metric("New Route Alerts", new_reports)
        
        st.divider()
        st.subheader("All Buses")
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.bar_chart(df["status"].value_counts())
        else:
            st.info("No buses found.")
            
        st.divider()
        st.subheader("Fleet Map")
        if not df.empty:
            m = folium.Map(location=[12.95, 80.18], zoom_start=11)
            for _, b in df.iterrows():
                folium.Marker(
                    [b["latitude"], b["longitude"]],
                    popup=f"{b['bus_no']}<br>{b['driver']}<br>{b['route_no']} – {b['route_name']}<br>{b['status']}",
                    tooltip=b["bus_no"],
                    icon=folium.Icon(
                        color="green" if b["status"] == "Moving" else "red",
                        icon="bus", prefix="fa"
                    )
                ).add_to(m)
            st_folium(m, width=None, height=470, key="admin_fleet_map")
            
    # ---------- TRACK BUS ----------
    elif page == "Track Bus":
        st.subheader("Track & Simulate")
        if df.empty:
            st.warning("No buses available.")
        else:
            bus_number = st.selectbox("Select Bus", df["bus_no"].tolist())
            bus = get_bus_details(bus_number)
            if bus:
                bus_no, driver, route_no, route_name, lat, lon, speed, status = bus
                c1, c2 = st.columns(2)
                c1.metric("Bus", bus_no)
                c2.metric("Status", status)
                c3, c4 = st.columns(2)
                c3.metric("Driver", driver)
                c4.metric("Speed", f"{speed} km/h")
                st.write(f"**Route:** {route_no} – {route_name}")
                
                if bus_no not in st.session_state.eta_by_bus:
                    st.session_state.eta_by_bus[bus_no] = random.randint(5, 20)
                st.info(f"ETA: {st.session_state.eta_by_bus[bus_no]} minutes")
                
                m = folium.Map(location=[lat, lon], zoom_start=14)
                folium.Marker(
                    [lat, lon], popup=bus_no,
                    icon=folium.Icon(color="green" if status == "Moving" else "red", icon="bus", prefix="fa")
                ).add_to(m)
                st_folium(m, width=None, height=420, key="admin_single_bus_map")
                
                if st.button("Simulate Movement", use_container_width=True):
                    new_lat = lat + random.uniform(-0.002, 0.002)
                    new_lon = lon + random.uniform(-0.002, 0.002)
                    new_speed = random.randint(20, 45)
                    conn.execute("""
                        UPDATE buses SET latitude=?, longitude=?, speed=?, status=?
                        WHERE bus_no=?
                    """, (new_lat, new_lon, new_speed, "Moving", bus_no))
                    conn.commit()
                    st.success("Location updated.")
                    st.rerun()
                    
    # ---------- BUS MANAGEMENT ----------
    elif page == "Bus Management":
        st.subheader("Bus Management")
        t1, t2, t3 = st.tabs(["Add Bus", "Update Bus", "Delete Bus"])
        
        with t1:
            with st.form("add_bus"):
                nb = st.text_input("Bus Number")
                nd = st.text_input("Driver Name")
                rno = st.text_input("Route Number (e.g. R-13)")
                rname = st.text_input("Route Name")
                nlat = st.number_input("Latitude", value=12.9350, format="%.6f")
                nlon = st.number_input("Longitude", value=80.1300, format="%.6f")
                submitted = st.form_submit_button("Add Bus")
                if submitted:
                    if nb.strip() and nd.strip() and rno.strip() and rname.strip():
                        try:
                            conn.execute(
                                "INSERT INTO buses (bus_no, driver, route_no, route_name, latitude, longitude, speed, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (nb.strip(), nd.strip(), rno.strip(), rname.strip(), nlat, nlon, 0, "Stopped")
                            )
                            conn.commit()
                            st.success(f"Bus {nb} added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding bus: {e}")
                    else:
                        st.warning("Please fill in all required fields.")

        with t2:
            buses_list = df["bus_no"].tolist() if not df.empty else []
            if not buses_list:
                st.info("No buses available to update.")
            else:
                with st.form("update_bus_form"):
                    sel_bus = st.selectbox("Select Bus to Update", buses_list)
                    current_bus = get_bus_details(sel_bus)
                    udriver = st.text_input("Driver Name", value=current_bus[1])
                    uroute_no = st.text_input("Route Number", value=current_bus[2])
                    uroute_name = st.text_input("Route Name", value=current_bus[3])
                    ustatus = st.selectbox("Status", ["Moving", "Stopped"], index=0 if current_bus[7] == "Moving" else 1)
                    upd_submitted = st.form_submit_button("Update Bus")
                    if upd_submitted:
                        conn.execute("""
                            UPDATE buses SET driver=?, route_no=?, route_name=?, status=? WHERE bus_no=?
                        """, (udriver, uroute_no, uroute_name, ustatus, sel_bus))
                        conn.commit()
                        st.success(f"Bus {sel_bus} updated successfully!")
                        st.rerun()

        with t3:
            buses_list = df["bus_no"].tolist() if not df.empty else []
            if not buses_list:
                st.info("No buses available to delete.")
            else:
                with st.form("delete_bus_form"):
                    del_bus = st.selectbox("Select Bus to Delete", buses_list, key="del_bus_sel")
                    del_submitted = st.form_submit_button("Delete Bus")
                    if del_submitted:
                        conn.execute("DELETE FROM buses WHERE bus_no = ?", (del_bus,))
                        conn.commit()
                        st.success(f"Bus {del_bus} deleted successfully!")
                        st.rerun()

    # ---------- STUDENT MANAGEMENT ----------
    elif page == "Student Management":
        st.subheader("Student Records")
        students_df = get_students()
        if not students_df.empty:
            st.dataframe(students_df, use_container_width=True, hide_index=True)
        else:
            st.info("No student records found.")
        
        st.markdown("---")
        with st.form("add_student_form"):
            st.subheader("Enroll New Student")
            adm = st.text_input("Admission Number (e.g. 1051)")
            sname = st.text_input("Student Name")
            bno = st.selectbox("Assign Bus", df["bus_no"].tolist() if not df.empty else [])
            pickup = st.text_input("Pickup Point")
            parent = st.text_input("Parent Username (must match login)")
            grade = st.text_input("Grade / Class")
            if st.form_submit_button("Enroll Student"):
                if adm.strip() and sname.strip() and parent.strip():
                    try:
                        conn.execute(
                            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
                            (adm.strip(), sname.strip(), bno, pickup.strip(), parent.strip().lower(), grade.strip())
                        )
                        conn.commit()
                        st.success(f"Student {sname} enrolled successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error enrolling student: {e}")
                else:
                    st.warning("Please fill in all required fields.")

    # ---------- NOTIFICATIONS ----------
    elif page == "Notifications":
        st.subheader("Pending Leave Requests")
        leaves_df = pd.read_sql_query("SELECT * FROM leave_requests WHERE status = 'Pending'", conn)
        if not leaves_df.empty:
            for _, row in leaves_df.iterrows():
                with st.container():
                    st.write(f"**Student:** {row['student_name']} (Adm: {row['admission_no']}) | **Bus:** {row['bus_no']}")
                    st.write(f"**Date:** {row['leave_date']} | **Reason:** {row['reason']}")
                    col1, col2 = st.columns(2)
                    if col1.button(f"Approve {row['leave_id']}", key=f"app_{row['leave_id']}"):
                        conn.execute("UPDATE leave_requests SET status = 'Approved' WHERE leave_id = ?", (row['leave_id'],))
                        conn.commit()
                        st.success("Leave approved.")
                        st.rerun()
                    if col2.button(f"Reject {row['leave_id']}", key=f"rej_{row['leave_id']}"):
                        conn.execute("UPDATE leave_requests SET status = 'Rejected' WHERE leave_id = ?", (row['leave_id'],))
                        conn.warning("Leave rejected.")
                        st.rerun()
                    st.divider()
        else:
            st.info("No pending leave requests.")
            
        st.subheader("Route Reports from Parents")
        reports_df = pd.read_sql_query("SELECT * FROM route_reports WHERE report_status = 'New'", conn)
        if not reports_df.empty:
            for _, row in reports_df.iterrows():
                st.write(f"**Bus:** {row['bus_no']} | **Student:** {row['student_name']} | **Parent:** {row['parent_username']}")
                st.write(f"**Description:** {row['description']}")
                if st.button(f"Mark Resolved {row['report_id']}", key=f"rep_{row['report_id']}"):
                    conn.execute("UPDATE route_reports SET report_status = 'Resolved' WHERE report_id = ?", (row['report_id'],))
                    conn.commit()
                    st.success("Report marked as resolved.")
                    st.rerun()
                st.divider()
        else:
            st.info("No new route reports.")
