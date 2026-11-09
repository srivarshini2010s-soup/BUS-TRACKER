    background: #0F382E;
    border-radius: 12px;
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
    # Multi-child parents (Parents with 2-3 children)
    "vijay.sethupathi":   {"password": _h("Vijay@2017"),   "role": "parent"},
    "nayanthara.nair":    {"password": _h("Nayan@2018"),    "role": "parent"},
    "suriya.sivakumar":   {"password": _h("Suriya@2016"),   "role": "parent"},
    "keerthy.suresh":     {"password": _h("Keerthy@2019"), "role": "parent"},
    "dhanush.r":          {"password": _h("Dhanush@2017"), "role": "parent"},
    "sai.pallavi":        {"password": _h("Sai@2020"),      "role": "parent"},
    "sivakarthikeyan.s":  {"password": _h("SK@2018"),       "role": "parent"},
    "trisha.krishnan":    {"password": _h("Trisha@2015"),   "role": "parent"},
    "karthi.sivakumar":   {"password": _h("Karthi@2019"),   "role": "parent"},
    # Single-child parents (Remaining up to 40 total parents)
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

def table_columns(table_name):
    """Return the column names for a SQLite table."""
    return [
        row[1]
        for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    ]


def ensure_table_type_and_columns(table_name, expected_columns, create_sql):
    """
    Ensure that an object with this name is a table with the expected schema.
    Rebuild only incompatible tables so old deployment databases do not crash.
    """
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
