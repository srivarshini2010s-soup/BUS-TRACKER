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
    initial_sidebar_state="expanded"
)

# ==========================================================
# 2. DATABASE
# ==========================================================
DB_PATH = Path(__file__).resolve().parent / "bus_tracking.db"
conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)

# ==========================================================
# 3. DARK LUXURY THEME
# ==========================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #0B1312 !important; color: #F5F5F3 !important; }
[data-testid="stHeader"] { background: #0B1312 !important; }
h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important; color: #F5F5F3 !important;
}
p, label, span, li, .stMarkdown, .stCaption,
[data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"] { color: #F5F5F3 !important; }
section[data-testid="stSidebar"] { background-color: #0F382E !important; }
section[data-testid="stSidebar"] * { color: #F5F5F3 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: #D4AF37 !important; color: #0B1312 !important;
    border-radius: 10px !important; font-weight: 700 !important; border: none !important;
}
div[data-testid="stMetric"] {
    background: #0F382E !important; border: 1px solid #D4AF37 !important;
    border-radius: 14px !important; padding: 16px !important; min-width: 0 !important;
}
div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
    color: #D4AF37 !important; font-weight: 600 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #F5F5F3 !important; font-weight: 700 !important; overflow-wrap: anywhere !important;
}
.stButton > button, .stFormSubmitButton > button {
    background: #D4AF37 !important; color: #0B1312 !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important; min-height: 42px !important;
    white-space: normal !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: #E8C547 !important; color: #0B1312 !important;
}
input, textarea, select, .stTextInput input, .stTextArea textarea, .stDateInput input,
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
    background-color: #0F382E !important; color: #F5F5F3 !important;
    -webkit-text-fill-color: #F5F5F3 !important; border-radius: 10px !important;
    border: 1px solid #D4AF37 !important; opacity: 1 !important;
}
input::placeholder, textarea::placeholder, ::-webkit-input-placeholder {
    color: #A0B2AC !important; -webkit-text-fill-color: #A0B2AC !important; opacity: 1 !important;
}
button[aria-label="Show password"], button[aria-label="Hide password"],
button[aria-label*="password"] svg { color: #D4AF37 !important; fill: #D4AF37 !important; }
div[data-baseweb="select"] { background-color: #0F382E !important; border-radius: 10px !important; }
div[data-baseweb="select"] > div {
    background-color: #0F382E !important; color: #F5F5F3 !important;
    border: 1px solid #D4AF37 !important; border-radius: 10px !important;
}
div[data-baseweb="select"] * {
    color: #F5F5F3 !important; -webkit-text-fill-color: #F5F5F3 !important;
}
ul[data-baseweb="menu"] { background-color: #0F382E !important; border: 1px solid #D4AF37 !important; }
ul[data-baseweb="menu"] li, ul[data-baseweb="menu"] li * {
    background-color: #0F382E !important; color: #F5F5F3 !important;
    -webkit-text-fill-color: #F5F5F3 !important;
}
ul[data-baseweb="menu"] li:hover { background-color: #1A4A3C !important; }
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label, [data-testid="stSelectbox"] label,
[data-testid="stDateInput"] label { color: #D4AF37 !important; font-weight: 600 !important; }
[data-testid="stTabs"] button { color: #F5F5F3 !important; font-weight: 600 !important; }
.login-card {
    background: #0F382E !important; border-radius: 20px; padding: 30px 24px;
