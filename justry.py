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
# 2. CSS STYLING (PROPERLY WRAPPED IN st.markdown)
# ==========================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
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
.stButton > button, .stFormSubmitButton > button { 
    background: #D4AF37 !important; 
    color: #0B1312 !important; 
    border: none !important; 
    border-radius: 10px !important; 
    font-weight: 700 !important; 
    padding: 10px 20px !important; 
} 
.stButton > button:hover, .stFormSubmitButton > button:hover { 
    background: #E8C547 !important; 
    color: #0B1312 !important; 
}

/* Mobile Input, Textarea, and Select Overrides */ 
input, textarea, select, .stTextInput input, .stTextArea textarea, .stDateInput input, [data-baseweb="input"] input { 
    background-color: #0F382E !important; 
    color: #F5F5F3 !important; 
    -webkit-text-fill-color: #F5F5F3 !important; 
    border-radius: 10px !important; 
    border: 1px solid #D4AF37 !important; 
    opacity: 1 !important; 
}

/* Placeholders Visibility Fix */ 
::placeholder, ::-webkit-input-placeholder { 
    color: #A0B2AC !important; 
    -webkit-text-fill-color: #A0B2AC !important; 
    opacity: 1 !important; 
}

/* Password Eye Icon & Native SVG Controls Fix */ 
button[aria-label="Show password"], button[aria-label="Hide password"], svg[data-icon="eye"], svg[data-icon="eye-slash"] { 
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
ul[data-baseweb="menu"] li, ul[data-baseweb="menu"] li * { 
    background-color: #0F382E !important; 
    color: #F5F5F3 !important; 
    -webkit-text-fill-color: #F5F5F3 !important; 
} 
ul[data-baseweb="menu"] li:hover { 
    background-color: #1A4A3C !important; 
}

/* Labels Fix */ 
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label, [data-testid="stNumberInput"] label, [data-testid="stSelectbox"] label, [data-testid="stDateInput"] label { 
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
