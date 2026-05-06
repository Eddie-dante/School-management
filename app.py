# app.py - SRMS - School Resource Management System by WeGEM
# Integrated with Supabase
import streamlit as st
import pandas as pd
import json
import hashlib
from datetime import datetime, timedelta
import random
import string
import base64
from io import BytesIO
import qrcode
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import time
import supabase

# ============ SUPABASE CONFIGURATION ============
SUPABASE_URL = "https://mcjkdnhbbnxvvgnjbuzy.supabase.co"
SUPABASE_SECRET = "sb_secret_o1cZAZTjzwpFJxwXswr5ig_IGPU3uh3"
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_SECRET)

TABLE_MAP = {
    "books": "books",
    "members": "members",
    "borrowed": "borrowed",
    "teachers": "teachers",
    "classes": "classes",
    "furniture": "furniture",
    "audit_log": "audit_log",
    "chat_messages": "chat_messages",
    "forum_messages": "forum_messages",
    "notepad": "notepad",
    "attachments": "chat_messages"  # attachments are stored inside chat_messages now
}

def load_data(filename, default=None):
    """Load data from Supabase, mimicking the old JSON file structure."""
    try:
        base = filename.rsplit(".json", 1)[0]
        if "_" in base:
            data_type, school = base.rsplit("_", 1)
        else:
            data_type, school = base, None

        if data_type in TABLE_MAP:
            table = TABLE_MAP[data_type]
            if school:
                resp = supabase_client.table(table).select("*").eq("school_name", school).execute()
            else:
                resp = supabase_client.table(table).select("*").execute()
            return resp.data if resp.data else (default if default is not None else [])
        elif filename == "schools.json":
            resp = supabase_client.table("schools").select("*").execute()
            schools_dict = {}
            for row in resp.data:
                schools_dict[row['name']] = row
            return schools_dict if schools_dict else (default if default is not None else {})
        else:
            return default if default is not None else []
    except Exception as e:
        st.error(f"Database read error ({filename}): {e}")
        return default if default is not None else []

def save_data(filename, data):
    """Save data to Supabase, replacing old JSON file writes."""
    try:
        base = filename.rsplit(".json", 1)[0]
        if "_" in base:
            data_type, school = base.rsplit("_", 1)
        else:
            data_type, school = base, None

        if data_type in TABLE_MAP:
            table = TABLE_MAP[data_type]
            if school:
                # Remove all records for this school and re‑insert (simplistic but works)
                supabase_client.table(table).delete().eq("school_name", school).execute()
                if isinstance(data, list) and data:
                    for item in data:
                        item['school_name'] = school
                    supabase_client.table(table).insert(data).execute()
        elif filename == "schools.json":
            for sname, sdata in data.items():
                sdata['name'] = sname
                supabase_client.table("schools").upsert(sdata, on_conflict="name").execute()
    except Exception as e:
        st.error(f"Database write error ({filename}): {e}")

# ============ REST OF ORIGINAL CODE (UNCHANGED LOGIC, JUST DATA LAYER REPLACED) ============

# Page config
st.set_page_config(
    page_title="SRMS - School Resource Management System",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ 100+ WALLPAPERS ============
WALLPAPERS = {
    "None": "",
    # School & Education
    "Library": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1920",
    "Classroom": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=1920",
    "School Building": "https://images.unsplash.com/photo-1577896851231-70ef18881754?w=1920",
    "Study Desk": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1920",
    "Bookshelf": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1920",
    "Graduation": "https://images.unsplash.com/photo-1523050854058-8df90910f68e?w=1920",
    
    # Nature & Landscapes
    "Sunset": "https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=1920",
    "Ocean": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1920",
    "Forest": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1920",
    "Mountain": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920",
    "Desert": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=1920",
    "Waterfall": "https://images.unsplash.com/photo-1544551763-46a013bb70b5?w=1920",
    "Cherry Blossom": "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=1920",
    "Lavender Field": "https://images.unsplash.com/photo-1499002238440-d264edd596ec?w=1920",
    "Autumn Forest": "https://images.unsplash.com/photo-1507783548227-544c3b8fc065?w=1920",
    "Winter Snow": "https://images.unsplash.com/photo-1477601263568-180e2c6d046e?w=1920",
    "Spring Meadow": "https://images.unsplash.com/photo-1490750967868-88aa4cef14d0?w=1920",
    "Summer Field": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1920",
    "Tropical Beach": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1920",
    "Mountain Lake": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920",
    "Foggy Forest": "https://images.unsplash.com/photo-1485230405346-71acb9518d9b?w=1920",
    "Golden Hour": "https://images.unsplash.com/photo-1501856777435-29877ed80a3d?w=1920",
    "Blue Lagoon": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1920",
    "Zen Garden": "https://images.unsplash.com/photo-1545389336-cf090694435e?w=1920",
    "Palm Trees": "https://images.unsplash.com/photo-1509233725247-49e657c54213?w=1920",
    "Savanna": "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=1920",
    "Iceberg": "https://images.unsplash.com/photo-1540979388789-7cee28a1cdc9?w=1920",
    
    # City & Architecture
    "City Lights": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1920",
    "Neon City": "https://images.unsplash.com/photo-1557682257-2f9c97a8a469?w=1920",
    "Bridge Night": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1920",
    "Modern Building": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=1920",
    "Tokyo Street": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1920",
    "New York": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=1920",
    
    # Space & Abstract
    "Galaxy": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1920",
    "Milky Way": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920",
    "Starfield": "https://images.unsplash.com/photo-1557683320-2d5001d5e9c5?w=1920",
    "Aurora": "https://images.unsplash.com/photo-1483347756197-71ef80e95f73?w=1920",
    "Nebula": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1920",
    "Abstract Waves": "https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=1920",
    "Geometric": "https://images.unsplash.com/photo-1557683311-eac922347aa1?w=1920",
    "Color Splash": "https://images.unsplash.com/photo-1557683304-6733ba7e4d6f?w=1920",
    "Purple Haze": "https://images.unsplash.com/photo-1557682257-2f9c97a8a469?w=1920",
    "Rainbow": "https://images.unsplash.com/photo-1511300636408-a63a89df3482?w=1920",
    "Clouds": "https://images.unsplash.com/photo-1501630834273-4b5604d2ee31?w=1920",
    "Stars": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920",
    "Starry Night": "https://images.unsplash.com/photo-1557683320-2d5001d5e9c5?w=1920",
    "Nature Leaves": "https://images.unsplash.com/photo-1557683316-973673baf926?w=1920",
    
    # Anime Style (5 wallpapers)
    "Anime Sunset": "https://images.unsplash.com/photo-1578632767115-351597cf1bfe?w=1920",
    "Anime Sky": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1920",
    "Anime City": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1920",
    "Anime Garden": "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=1920",
    "Anime Night": "https://images.unsplash.com/photo-1557682257-2f9c97a8a469?w=1920",
    
    # Additional Beautiful Wallpapers
    "Coral Reef": "https://images.unsplash.com/photo-1544551763-46a013bb70b5?w=1920",
    "Bamboo Forest": "https://images.unsplash.com/photo-1518531933039-315f5d4a6b1a?w=1920",
    "Volcano": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1920",
    "Canyon": "https://images.unsplash.com/photo-1474044159687-1ee9f3a51722?w=1920",
    "Northern Lights": "https://images.unsplash.com/photo-1483347756197-71ef80e95f73?w=1920",
    "Sunflower Field": "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=1920",
    "Rose Garden": "https://images.unsplash.com/photo-1490750967868-88aa4cef14d0?w=1920",
    "Rainforest": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1920",
    "Alps": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1920",
    "Sahara": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=1920",
}

# ============ EMOJI PICKER ============
EMOJI_CATEGORIES = {
    "😀 Smileys": ["😀", "😃", "😄", "😁", "😅", "😂", "🤣", "😊", "😇", "🙂", "😉", "😌", "😍", "🥰", "😘", "😗", "😋", "😛", "😜", "🤪", "😝", "🤑", "🤗", "🤭", "🤫", "🤔", "🤐", "🤨", "😐", "😑", "😶", "😏", "😒", "🙄", "😬", "😮", "😯", "😲", "😳", "🥺", "😢", "😭", "😤", "😡", "🤬", "😈", "👿", "💀", "☠️"],
    "👍 Gestures": ["👍", "👎", "👌", "✌️", "🤞", "🤟", "🤘", "🤙", "👈", "👉", "👆", "👇", "☝️", "✋", "🤚", "🖐️", "🖖", "👋", "🤏", "✍️", "👏", "🙌", "🫶", "🤝", "🙏"],
    "❤️ Hearts": ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟"],
    "📚 School": ["📚", "📖", "📝", "✏️", "🖊️", "📏", "📐", "🎓", "🏫", "📋", "📎", "🖇️", "🗂️", "📁", "📌", "📍", "✂️", "🖍️"],
    "🎯 Objects": ["🎯", "⭐", "🌟", "✨", "🔥", "💯", "✅", "❌", "⚠️", "🔔", "🔕", "📢", "📣", "💡", "🔦", "💰", "🎁", "🏆", "🥇", "🥈", "🥉", "📅", "⏰", "🔑", "🔒", "🔓"],
}

def get_premium_css(wallpaper=None):
    wallpaper_url = WALLPAPERS.get(wallpaper, "")
    bg_style = f"background-image: url('{wallpaper_url}'); background-size: cover; background-position: center; background-attachment: fixed;" if wallpaper_url else "background: linear-gradient(135deg, #0a0e27, #1a1f4e, #0f3460);"
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        * {{ font-family: 'Inter', sans-serif; }}
        
        .stApp {{ {bg_style} }}
        .stApp > header {{ background: rgba(10,14,39,0.85) !important; backdrop-filter: blur(30px) !important; border-bottom: 2px solid rgba(212,175,55,0.3) !important; }}
        .main .block-container {{ background: rgba(10,14,39,0.5) !important; backdrop-filter: blur(25px) !important; border-radius: 20px !important; padding: 2rem !important; margin: 1rem !important; border: 1px solid rgba(212,175,55,0.2) !important; }}
        
        section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0a0e27 0%, #1a1f4e 50%, #0f3460 100%) !important; }}
        section[data-testid="stSidebar"] > div {{ background: rgba(0,0,0,0.4) !important; padding: 1rem !important; }}
        section[data-testid="stSidebar"] * {{ color: #FFFFFF !important; text-shadow: 0 1px 3px rgba(0,0,0,0.5) !important; }}
        section[data-testid="stSidebar"] .stButton button {{ background: rgba(255,255,255,0.1) !important; border: 1px solid rgba(212,175,55,0.3) !important; color: #FFFFFF !important; text-align: left !important; padding: 10px 15px !important; margin: 2px 0 !important; font-size: 0.9rem !important; box-shadow: none !important; }}
        section[data-testid="stSidebar"] .stButton button:hover {{ background: rgba(233,69,96,0.4) !important; border-color: rgba(233,69,96,0.6) !important; }}
        section[data-testid="stSidebar"] .streamlit-expanderHeader {{ background: rgba(212,175,55,0.2) !important; border: 1px solid rgba(212,175,55,0.3) !important; color: #FFD700 !important; font-weight: 700 !important; }}
        
        .main .block-container h1, .main .block-container h2, .main .block-container h3, .main .block-container h4 {{ color: #FFFFFF !important; text-shadow: 0 2px 10px rgba(0,0,0,0.6) !important; }}
        .main .block-container p, .main .block-container span, .main .block-container label {{ color: #FFFFFF !important; text-shadow: 0 1px 3px rgba(0,0,0,0.5) !important; }}
        
        .glass-card {{ background: rgba(255,255,255,0.12) !important; backdrop-filter: blur(20px) !important; border-radius: 16px !important; padding: 25px !important; margin: 15px 0 !important; border: 1px solid rgba(212,175,55,0.25) !important; box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important; }}
        .stat-card {{ background: rgba(255,255,255,0.08) !important; backdrop-filter: blur(15px) !important; padding: 25px !important; border-radius: 16px !important; border-left: 4px solid #e94560 !important; border: 1px solid rgba(255,255,255,0.15) !important; text-align: center !important; margin: 8px 0 !important; }}
        .stat-value {{ font-size: 2.5em !important; font-weight: 900 !important; color: #FFFFFF !important; }}
        .stat-label {{ color: rgba(255,255,255,0.75) !important; font-size: 0.9em !important; font-weight: 600 !important; }}
        
        .stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input {{ background: rgba(255,255,255,0.95) !important; border: 2px solid rgba(212,175,55,0.4) !important; border-radius: 10px !important; padding: 10px 15px !important; color: #1a1a1a !important; font-weight: 500 !important; }}
        .stTextInput input::placeholder {{ color: #999 !important; }}
        .stSelectbox > div > div {{ background: rgba(255,255,255,0.95) !important; border: 2px solid rgba(212,175,55,0.4) !important; border-radius: 10px !important; }}
        .stSelectbox [data-baseweb="select"] * {{ color: #1a1a1a !important; }}
        
        .stButton button {{ background: linear-gradient(135deg, #e94560, #c62a47) !important; border: none !important; border-radius: 10px !important; color: white !important; font-weight: 600 !important; padding: 10px 20px !important; box-shadow: 0 4px 15px rgba(233,69,96,0.3) !important; transition: all 0.3s ease !important; }}
        .stButton button:hover {{ transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(233,69,96,0.5) !important; }}
        
        .stDataFrame {{ background: rgba(255,255,255,0.08) !important; backdrop-filter: blur(15px) !important; border-radius: 12px !important; border: 1px solid rgba(212,175,55,0.3) !important; }}
        .stDataFrame th {{ background: rgba(233,69,96,0.8) !important; color: #FFFFFF !important; font-weight: 700 !important; }}
        .stDataFrame td {{ background: rgba(255,255,255,0.05) !important; color: #FFFFFF !important; }}
        
        .school-code-banner {{ background: rgba(255,255,255,0.1) !important; backdrop-filter: blur(15px) !important; border: 2px dashed rgba(233,69,96,0.4) !important; border-radius: 16px !important; padding: 25px !important; text-align: center !important; }}
        .invite-code {{ font-family: 'Courier New', monospace !important; font-size: 2.5em !important; font-weight: 800 !important; letter-spacing: 8px !important; color: #FFFFFF !important; }}
        
        .stTabs [data-baseweb="tab-list"] {{ background: rgba(255,255,255,0.08) !important; border-radius: 12px !important; padding: 4px !important; }}
        .stTabs [data-baseweb="tab"] {{ color: rgba(255,255,255,0.7) !important; }}
        .stTabs [aria-selected="true"] {{ background: #e94560 !important; color: #FFFFFF !important; border-radius: 8px !important; }}
        
        .emoji-btn {{ font-size: 1.5em !important; padding: 5px 10px !important; cursor: pointer !important; background: transparent !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 8px !important; margin: 2px !important; transition: all 0.2s ease !important; }}
        .emoji-btn:hover {{ background: rgba(233,69,96,0.3) !important; transform: scale(1.2) !important; }}
        
        .forum-message {{ background: rgba(255,255,255,0.08) !important; backdrop-filter: blur(10px) !important; border-radius: 12px !important; padding: 12px 16px !important; margin: 8px 0 !important; border: 1px solid rgba(255,255,255,0.15) !important; }}
        .forum-message:hover {{ background: rgba(255,255,255,0.12) !important; }}
        
        @media (max-width: 768px) {{ .main .block-container {{ padding: 1rem !important; margin: 0.5rem !important; }} }}
    </style>
    """

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'school' not in st.session_state:
    st.session_state.school = None
if 'page' not in st.session_state:
    st.session_state.page = 'startup'
if 'wallpaper' not in st.session_state:
    st.session_state.wallpaper = "Library"
if 'current_section' not in st.session_state:
    st.session_state.current_section = 'dashboard'
if 'action' not in st.session_state:
    st.session_state.action = None
if 'show_admin_secret' not in st.session_state:
    st.session_state.show_admin_secret = False
if 'secret_key_combo' not in st.session_state:
    st.session_state.secret_key_combo = ""
if 'selected_emoji' not in st.session_state:
    st.session_state.selected_emoji = ""

st.markdown(get_premium_css(st.session_state.wallpaper), unsafe_allow_html=True)

def generate_code(prefix="", length=8):
    chars = string.ascii_uppercase + string.digits
    return prefix + ''.join(random.choices(chars, k=length))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_admin():
    return st.session_state.user and st.session_state.user.get('role') == 'admin'

def add_audit_entry(action, details):
    school_name = st.session_state.school['name']
    audit_log = load_data(f"audit_log_{school_name}.json", [])
    audit_log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": st.session_state.user['name'],
        "action": action,
        "details": details
    })
    if len(audit_log) > 500:
        audit_log = audit_log[-500:]
    save_data(f"audit_log_{school_name}.json", audit_log)

def check_duplicate_assignment(school_name, adm, item_type, item_number):
    """Check if a student already has an item assigned"""
    if item_type == 'book':
        borrowed = load_data(f"borrowed_{school_name}.json", [])
        return any(b for b in borrowed if b.get('adm') == adm and b.get('bookNo') == item_number and not b.get('returned'))
    elif item_type == 'chair':
        furniture = load_data(f"furniture_{school_name}.json", [])
        return any(f for f in furniture if f.get('adm') == adm and f.get('chair') == item_number and not f.get('returned'))
    elif item_type == 'locker':
        furniture = load_data(f"furniture_{school_name}.json", [])
        return any(f for f in furniture if f.get('adm') == adm and f.get('locker') == item_number and not f.get('returned'))
    return False

# ============== STARTUP PAGE ==============
def startup_page():
    st.markdown("""
    <div class="glass-card" style="text-align: center; max-width: 600px; margin: 50px auto;">
        <div style="width: 160px; height: 160px; background: linear-gradient(135deg, #d4af37, #f0d060, #d4af37); 
             border-radius: 35px; display: inline-flex; align-items: center; justify-content: center; 
             font-size: 55px; font-weight: 900; color: #0a0e27; margin-bottom: 20px;
             box-shadow: 0 20px 60px rgba(212, 175, 55, 0.4);">
            SRMS
        </div>
        <h1 style="font-size: 3.5em; background: linear-gradient(180deg, #f0d060, #d4af37, #b8941f); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 10px 0;">
            SRMS
        </h1>
        <p style="font-size: 1.4em; color: #FFFFFF; margin: 10px 0;">School Resource Management System</p>
        <p style="color: #d4af37; font-size: 1.1em;">by <span style="color: #f0d060; font-weight: 700;">WeGEM</span> (Edwin)</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔑 Staff Login", use_container_width=True, key="btn_login"):
            st.session_state.action = 'login'
    with col2:
        if st.button("📝 Staff Sign Up", use_container_width=True, key="btn_signup"):
            st.session_state.action = 'signup'
    with col3:
        if st.button("🏫 Create School", use_container_width=True, key="btn_create"):
            st.session_state.action = 'create'
    
    if st.session_state.action:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        if st.session_state.action == 'login':
            login_form()
        elif st.session_state.action == 'signup':
            signup_form()
        elif st.session_state.action == 'create':
            create_school_form()
        st.markdown('</div>', unsafe_allow_html=True)

def login_form():
    st.markdown('<h3 style="color:#FFFFFF;">🔐 Staff Login</h3>', unsafe_allow_html=True)
    with st.form("frm_login"):
        name = st.text_input("👤 Your Full Name", placeholder="Enter your registered name")
        school_name = st.text_input("🏢 School Name", placeholder="Enter school name")
        invite_code = st.text_input("🔑 Invite Code", placeholder="Enter invite code")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
        if st.form_submit_button("🔑 Login", use_container_width=True):
            schools = load_data("schools.json", {})
            school = schools.get(school_name)
            if not school:
                st.error("School not found!")
                return
            users = load_data(f"users_{school_name}.json", [])
            user = next((u for u in users if u['name'].lower() == name.lower() and u['code'] == invite_code.upper()), None)
            if not user or user['password'] != hash_password(password):
                st.error("Invalid credentials!")
                return
            st.session_state.user = user
            st.session_state.school = school
            st.session_state.page = 'dashboard'
            st.session_state.action = None
            add_audit_entry('Login', f"{user['name']} logged in as {user['role']}")
            st.rerun()

def signup_form():
    st.markdown('<h3 style="color:#FFFFFF;">📝 Staff Sign Up</h3>', unsafe_allow_html=True)
    with st.form("frm_signup"):
        name = st.text_input("👤 Full Name", placeholder="Your full name")
        email = st.text_input("📧 Email", placeholder="your@email.com")
        phone = st.text_input("📞 Phone", placeholder="+1234567890")
        school_name = st.text_input("🏢 School Name", placeholder="Your school name")
        invite_code = st.text_input("🔑 Invite Code", placeholder="From your admin")
        staff_id = st.text_input("👤 Staff ID (Optional)", placeholder="Employee ID")
        password = st.text_input("🔒 Create Password", type="password", placeholder="Min 6 characters")
        if st.form_submit_button("📝 Sign Up", use_container_width=True):
            schools = load_data("schools.json", {})
            school = schools.get(school_name)
            if not school:
                st.error("School not found!")
                return
            if school['invite_code'] != invite_code.upper():
                st.error("Invalid invite code!")
                return
            if len(password) < 6:
                st.error("Password min 6 chars!")
                return
            users = load_data(f"users_{school_name}.json", [])
            if any(u['email'] == email for u in users):
                st.error("Email already registered!")
                return
            new_user = {
                "name": name, "email": email, "phone": phone, "staff_id": staff_id,
                "code": invite_code.upper(), "password": hash_password(password),
                "role": "teacher", "joined": datetime.now().strftime("%Y-%m-%d")
            }
            users.append(new_user)
            save_data(f"users_{school_name}.json", users)
            st.session_state.user = new_user
            st.session_state.school = school
            st.session_state.page = 'dashboard'
            st.session_state.action = None
            add_audit_entry('Signup', f"{name} signed up as teacher")
            st.success("Registration successful!")
            st.rerun()

def create_school_form():
    st.markdown('<h3 style="color:#FFFFFF;">🏫 Create New School</h3>', unsafe_allow_html=True)
    with st.form("frm_create"):
        school_name = st.text_input("🏢 School Name", placeholder="e.g., Sunshine High School")
        address = st.text_input("📍 School Address", placeholder="School location")
        admin_name = st.text_input("👤 Admin Full Name", placeholder="Your full name")
        admin_email = st.text_input("📧 Admin Email", placeholder="admin@school.edu")
        admin_phone = st.text_input("📞 Admin Phone", placeholder="+1234567890")
        password = st.text_input("🔒 Password", type="password", placeholder="Min 8 characters")
        confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password")
        if st.form_submit_button("🚀 Create School", use_container_width=True):
            if password != confirm:
                st.error("Passwords don't match!")
                return
            if len(password) < 8:
                st.error("Password min 8 chars!")
                return
            schools = load_data("schools.json", {})
            if school_name in schools:
                st.error("School already exists!")
                return
            invite_code = generate_code()
            school = {
                "name": school_name, "address": address, "admin_name": admin_name,
                "admin_email": admin_email, "admin_phone": admin_phone,
                "invite_code": invite_code, "created": datetime.now().strftime("%Y-%m-%d")
            }
            schools[school_name] = school
            save_data("schools.json", schools)
            admin_user = {
                "name": admin_name, "email": admin_email, "phone": admin_phone,
                "staff_id": "ADMIN-001", "code": invite_code,
                "password": hash_password(password), "role": "admin",
                "joined": datetime.now().strftime("%Y-%m-%d")
            }
            save_data(f"users_{school_name}.json", [admin_user])
            # No need to pre-create empty files; the load function will return empty list on the first call
            st.session_state.user = admin_user
            st.session_state.school = school
            st.session_state.page = 'dashboard'
            st.session_state.action = None
            add_audit_entry('School Created', f"{school_name} created by {admin_name}")
            st.success(f"School created! Code: {invite_code}")
            st.rerun()

# ============== DASHBOARD ==============
def dashboard_page():
    school_name = st.session_state.school['name']
    user = st.session_state.user
    
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;margin-bottom:25px;">
        <h1 style="font-size:2.2em;">🏫 {school_name}</h1>
        <p style="font-size:1.1em;color:#FFFFFF;">👤 {user['name']} 
        <span style="background:{'#e94560' if user['role']=='admin' else '#0f3460'};color:#FFF;padding:4px 12px;border-radius:20px;font-size:0.8em;margin-left:10px;">{user['role'].upper()}</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    if is_admin():
        st.markdown(f"""
        <div class="school-code-banner">
            <p style="color:#FFF;font-size:0.9em;">🏫 School Invite Code - Share with Staff</p>
            <div class="invite-code">{st.session_state.school['invite_code']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # SIDEBAR
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:15px;background:rgba(255,255,255,0.08);border-radius:12px;margin-bottom:15px;border:1px solid rgba(212,175,55,0.3);">
            <div style="width:50px;height:50px;background:linear-gradient(135deg,#d4af37,#f0d060);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;color:#0a0e27;margin-bottom:8px;">{user['name'][0].upper()}</div>
            <p style="color:#FFFFFF;font-weight:700;margin:3px 0;">{user['name']}</p>
            <p style="color:#d4af37;font-size:0.8em;margin:3px 0;">{user['role'].upper()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🎨 Theme", expanded=False):
            wallpaper = st.selectbox("Wallpaper", list(WALLPAPERS.keys()), index=list(WALLPAPERS.keys()).index(st.session_state.wallpaper), key="side_wp")
            if wallpaper != st.session_state.wallpaper:
                st.session_state.wallpaper = wallpaper
                st.rerun()
        
        st.markdown("---")
        
        with st.expander("📊 MAIN", expanded=True):
            if st.button("📊 Dashboard", use_container_width=True, key="nav_dash"):
                st.session_state.current_section = 'dashboard'
                st.rerun()
        
        with st.expander("📖 LIBRARY", expanded=False):
            if st.button("📖 Book Issuing", use_container_width=True, key="nav_book_issue"):
                st.session_state.current_section = 'bookIssuing'
                st.rerun()
            if st.button("👤 Lend Book", use_container_width=True, key="nav_lend"):
                st.session_state.current_section = 'individualLending'
                st.rerun()
            if st.button("↩️ Returns", use_container_width=True, key="nav_returns"):
                st.session_state.current_section = 'return'
                st.rerun()
            if st.button("📋 Borrowed", use_container_width=True, key="nav_borrowed"):
                st.session_state.current_section = 'borrowedLog'
                st.rerun()
            if st.button("📚 Catalog", use_container_width=True, key="nav_catalog"):
                st.session_state.current_section = 'bookCatalog'
                st.rerun()
        
        with st.expander("🪑 RESOURCES", expanded=False):
            if st.button("🪑 Furniture", use_container_width=True, key="nav_furniture"):
                st.session_state.current_section = 'furnitureAllocation'
                st.rerun()
            if st.button("📱 QR Codes", use_container_width=True, key="nav_qr"):
                st.session_state.current_section = 'qr'
                st.rerun()
        
        with st.expander("👥 PEOPLE", expanded=False):
            if st.button("👥 Members", use_container_width=True, key="nav_members"):
                st.session_state.current_section = 'memberManagement'
                st.rerun()
            if st.button("👨‍🏫 Teachers", use_container_width=True, key="nav_teachers"):
                st.session_state.current_section = 'teacherAllocation'
                st.rerun()
            if st.button("📋 Classes", use_container_width=True, key="nav_classes"):
                st.session_state.current_section = 'classListManager'
                st.rerun()
        
        with st.expander("💬 COMMUNICATION", expanded=False):
            if st.button("💬 Private Chat", use_container_width=True, key="nav_chat"):
                st.session_state.current_section = 'chat'
                st.rerun()
            if st.button("📢 Group Forum", use_container_width=True, key="nav_forum"):
                st.session_state.current_section = 'forum'
                st.rerun()
            if st.button("📝 Notepad", use_container_width=True, key="nav_notepad"):
                st.session_state.current_section = 'notepad'
                st.rerun()
        
        with st.expander("📈 TOOLS", expanded=False):
            if st.button("🔍 Overview", use_container_width=True, key="nav_overview"):
                st.session_state.current_section = 'systemOverview'
                st.rerun()
            if st.button("📝 Log", use_container_width=True, key="nav_log"):
                st.session_state.current_section = 'auditLog'
                st.rerun()
            if st.button("📈 Reports", use_container_width=True, key="nav_reports"):
                st.session_state.current_section = 'reports'
                st.rerun()
        
        with st.expander("⚙️ SYSTEM", expanded=False):
            if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
                st.session_state.current_section = 'settings'
                st.rerun()
        
        # Secret admin key combo (simulated)
        if is_admin():
            st.markdown("---")
            with st.expander("🔐 Admin Secret", expanded=False):
                secret_input = st.text_input("Enter key combo:", placeholder="Ctrl+E+G+M code", key="admin_secret_key", type="password")
                if secret_input == "EGM":
                    if st.button("🔓 Unlock Private Chats", use_container_width=True, key="unlock_chats"):
                        st.session_state.show_admin_secret = True
                        st.success("🔓 Admin can now view all private chats!")
                        st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="nav_logout", type="primary"):
            add_audit_entry('Logout', st.session_state.user['name'])
            st.session_state.user = None
            st.session_state.school = None
            st.session_state.page = 'startup'
            st.rerun()
        
        st.markdown('<p style="color:rgba(255,255,255,0.4);font-size:0.7em;text-align:center;">SRMS v6.0 | by WeGEM (Edwin) | © 2025</p>', unsafe_allow_html=True)
    
    # MAIN CONTENT
    section = st.session_state.current_section
    
    if section == 'dashboard':
        render_dashboard()
    elif section == 'bookIssuing':
        render_book_issuing()
    elif section == 'individualLending':
        render_individual_lending()
    elif section == 'furnitureAllocation':
        render_furniture()
    elif section == 'return':
        render_returns()
    elif section == 'borrowedLog':
        render_borrowed()
    elif section == 'memberManagement':
        render_members()
    elif section == 'bookCatalog':
        render_catalog()
    elif section == 'teacherAllocation':
        render_teachers()
    elif section == 'classListManager':
        render_classes()
    elif section == 'qr':
        render_qr()
    elif section == 'chat':
        render_chat()
    elif section == 'forum':
        render_forum()
    elif section == 'notepad':
        render_notepad()
    elif section == 'systemOverview':
        render_system_overview()
    elif section == 'auditLog':
        render_audit_log()
    elif section == 'reports':
        render_reports()
    elif section == 'settings':
        render_settings()

# ============ EMOJI PICKER COMPONENT (fixed for persistence) ============
def emoji_picker(key_prefix=""):
    """Render an emoji picker and store selection in session state."""
    # If we want a callback approach (not used directly here, but used in render_chat)
    pass

# ============ RENDER FUNCTIONS (all remain the same except render_chat) ============

def render_dashboard():
    school_name = st.session_state.school['name']
    books = load_data(f"books_{school_name}.json", [])
    borrowed = load_data(f"borrowed_{school_name}.json", [])
    members = load_data(f"members_{school_name}.json", [])
    teachers = load_data(f"teachers_{school_name}.json", [])
    furniture = load_data(f"furniture_{school_name}.json", [])
    
    total_books = sum(b.get('quantity', 0) for b in books)
    books_borrowed = len([b for b in borrowed if not b.get('returned')])
    overdue_count = len([b for b in borrowed if not b.get('returned') and datetime.strptime(b.get('returnDate', '2000-01-01'), '%Y-%m-%d') < datetime.now()])
    
    st.markdown('<div class="glass-card"><h2>📊 Dashboard Overview</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_books}</div><div class="stat-label">Total Books</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{books_borrowed}</div><div class="stat-label">Books Borrowed</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_books - books_borrowed}</div><div class="stat-label">Books Available</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{len(members)}</div><div class="stat-label">Members</div></div>', unsafe_allow_html=True)
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{len(teachers)}</div><div class="stat-label">Teachers</div></div>', unsafe_allow_html=True)
    with col6:
        active_furniture = len([f for f in furniture if not f.get('returned')])
        st.markdown(f'<div class="stat-card"><div class="stat-value">{active_furniture}</div><div class="stat-label">Furniture Items</div></div>', unsafe_allow_html=True)
    with col7:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{overdue_count}</div><div class="stat-label">Overdue</div></div>', unsafe_allow_html=True)
    with col8:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{books_borrowed}</div><div class="stat-label">Active Loans</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_book_issuing():
    school_name = st.session_state.school['name']
    books = load_data(f"books_{school_name}.json", [])
    classes = load_data(f"classes_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>📖 Bulk Book Issuing to Class</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        book_options = [b['title'] for b in books if b.get('quantity', 0) > 0]
        selected_book = st.selectbox("Book:", book_options if book_options else ["No books available"], key="bi_book_select")
    with col2:
        class_options = [c['name'] for c in classes]
        selected_class = st.selectbox("Class:", class_options if class_options else ["No classes"], key="bi_class_select")
    
    col3, col4 = st.columns(2)
    with col3:
        issue_date = st.date_input("Issue Date:", datetime.now(), key="bi_issue_date_input")
    with col4:
        return_date = st.date_input("Return Date:", datetime.now() + timedelta(days=14), key="bi_return_date_input")
    
    filter_option = st.radio("Filter:", ["📋 All", "✅ Assigned", "❌ Unassigned"], horizontal=True, key="bi_filter")
    
    if st.button("📋 Load", use_container_width=True, key="bi_load_btn"):
        if selected_class != "No classes":
            class_data = next((c for c in classes if c['name'] == selected_class), None)
            if class_data:
                st.session_state.bi_students = class_data.get('students', [])
                st.success(f"Loaded {len(st.session_state.bi_students)} students!")
    
    if 'bi_students' in st.session_state:
        students = st.session_state.bi_students
        if students:
            borrowed = load_data(f"borrowed_{school_name}.json", [])
            df = pd.DataFrame(students)
            col_names = df.columns.tolist()
            name_col = col_names[0] if col_names else 'name'
            adm_col = col_names[1] if len(col_names) > 1 else 'adm'
            
            df['Book No'] = ""
            df['Status'] = "Pending"
            df['Issue'] = False
            
            for i, row in df.iterrows():
                adm = str(row.get(adm_col, ''))
                existing = next((b for b in borrowed if b.get('adm') == adm and b.get('bookTitle') == selected_book and not b.get('returned')), None)
                if existing:
                    df.at[i, 'Book No'] = existing.get('bookNo', '')
                    df.at[i, 'Status'] = '✓ Assigned'
            
            if filter_option == "✅ Assigned":
                df = df[df['Status'] == '✓ Assigned']
            elif filter_option == "❌ Unassigned":
                df = df[df['Status'] == 'Pending']
            
            edited_df = st.data_editor(df, use_container_width=True, key="bi_editor")
            
            if st.button("✅ Issue", use_container_width=True, key="bi_issue_btn"):
                count = 0
                for _, row in edited_df.iterrows():
                    if row.get('Issue') and row.get('Book No'):
                        adm = str(row.get(adm_col, ''))
                        book_no = str(row.get('Book No', ''))
                        
                        if check_duplicate_assignment(school_name, adm, 'book', book_no):
                            st.warning(f"⚠️ Student {row.get(name_col, '')} already has book #{book_no} assigned!")
                            continue
                        
                        book = next((b for b in books if b['title'] == selected_book), None)
                        if book and book['quantity'] > 0:
                            borrowed.append({
                                "name": str(row.get(name_col, '')),
                                "adm": adm,
                                "bookTitle": selected_book,
                                "bookNo": book_no,
                                "borrowDate": issue_date.strftime('%Y-%m-%d'),
                                "returnDate": return_date.strftime('%Y-%m-%d'),
                                "returned": False,
                                "id": generate_code("BOR")
                            })
                            book['quantity'] = book['quantity'] - 1
                            count = count + 1
                
                if count > 0:
                    save_data(f"borrowed_{school_name}.json", borrowed)
                    save_data(f"books_{school_name}.json", books)
                    add_audit_entry('Books Issued', f"{count} copies of '{selected_book}' to {selected_class}")
                    st.success(f"Issued {count} books!")
                    if 'bi_students' in st.session_state:
                        del st.session_state.bi_students
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_individual_lending():
    school_name = st.session_state.school['name']
    books = load_data(f"books_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>👤 Individual Book Lending</h2>', unsafe_allow_html=True)
    
    with st.form("frm_ind_lend"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name:", placeholder="Student name", key="il_name")
            adm = st.text_input("ADM:", placeholder="Admission number", key="il_adm")
            form = st.text_input("Form:", placeholder="Class/Form", key="il_form")
        with col2:
            stream = st.text_input("Stream:", placeholder="Stream", key="il_stream")
            book_options = [b['title'] for b in books if b.get('quantity', 0) > 0]
            selected_book = st.selectbox("Book:", book_options if book_options else ["No books"], key="il_book_select")
            book_no = st.text_input("Book No:", placeholder="Book number", key="il_book_no")
        
        col3, col4 = st.columns(2)
        with col3:
            borrow_date = st.date_input("Borrow Date:", datetime.now(), key="il_borrow_date")
        with col4:
            return_date = st.date_input("Return Date:", datetime.now() + timedelta(days=14), key="il_return_date")
        
        if st.form_submit_button("📖 Lend Book", use_container_width=True):
            if name and selected_book and selected_book != "No books" and book_no:
                if check_duplicate_assignment(school_name, adm, 'book', book_no):
                    st.error(f"❌ Student {name} already has book #{book_no} assigned!")
                else:
                    borrowed = load_data(f"borrowed_{school_name}.json", [])
                    book = next((b for b in books if b['title'] == selected_book), None)
                    if book and book['quantity'] > 0:
                        borrowed.append({
                            "name": name, "adm": adm, "form": form, "stream": stream,
                            "bookTitle": selected_book, "bookNo": book_no,
                            "borrowDate": borrow_date.strftime('%Y-%m-%d'),
                            "returnDate": return_date.strftime('%Y-%m-%d'),
                            "returned": False, "id": generate_code("BOR")
                        })
                        book['quantity'] = book['quantity'] - 1
                        save_data(f"borrowed_{school_name}.json", borrowed)
                        save_data(f"books_{school_name}.json", books)
                        add_audit_entry('Lend Book', f"{name} borrowed '{selected_book}' (#{book_no})")
                        st.success("Book lent successfully!")
                        st.rerun()
                    else:
                        st.error("Book not available!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_furniture():
    school_name = st.session_state.school['name']
    classes = load_data(f"classes_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>🪑 Furniture Allocation</h2>', unsafe_allow_html=True)
    
    class_options = [c['name'] for c in classes]
    if not class_options:
        st.warning("No classes available. Import class lists first.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    selected_class = st.selectbox("Class:", class_options, key="fur_class_select")
    
    col1, col2 = st.columns(2)
    with col1:
        chair_prefix = st.text_input("Chair Prefix:", "CH-", key="fur_chair_prefix")
        chair_start = st.number_input("Chair Start:", 1, 1000, 1, key="fur_chair_start")
        chair_end = st.number_input("Chair End:", 1, 1000, 10, key="fur_chair_end")
    with col2:
        locker_prefix = st.text_input("Locker Prefix:", "LK-", key="fur_locker_prefix")
        locker_start = st.number_input("Locker Start:", 1, 1000, 1, key="fur_locker_start")
        locker_end = st.number_input("Locker End:", 1, 1000, 10, key="fur_locker_end")
    
    alloc_date = st.date_input("Date:", datetime.now(), key="fur_alloc_date")
    
    filter_option = st.radio("Filter:", ["📋 All", "✅ Allocated", "❌ Pending"], horizontal=True, key="fur_filter")
    
    if st.button("📋 Load Class", use_container_width=True, key="fur_load_btn"):
        class_data = next((c for c in classes if c['name'] == selected_class), None)
        if class_data:
            st.session_state.fur_students = class_data.get('students', [])
            st.success(f"Loaded {len(st.session_state.fur_students)} students!")
    
    if 'fur_students' in st.session_state:
        students = st.session_state.fur_students
        if students:
            furniture = load_data(f"furniture_{school_name}.json", [])
            df = pd.DataFrame(students)
            col_names = df.columns.tolist()
            name_col = col_names[0] if col_names else 'name'
            adm_col = col_names[1] if len(col_names) > 1 else 'adm'
            
            df['Chair No'] = ""
            df['Locker No'] = ""
            df['Status'] = "Pending"
            df['Allocate'] = False
            
            for i, row in df.iterrows():
                adm = str(row.get(adm_col, ''))
                existing = next((f for f in furniture if f.get('adm') == adm and not f.get('returned')), None)
                if existing:
                    df.at[i, 'Chair No'] = existing.get('chair', '')
                    df.at[i, 'Locker No'] = existing.get('locker', '')
                    df.at[i, 'Status'] = '✓ Allocated'
            
            if filter_option == "✅ Allocated":
                df = df[df['Status'] == '✓ Allocated']
            elif filter_option == "❌ Pending":
                df = df[df['Status'] == 'Pending']
            
            edited_df = st.data_editor(df, use_container_width=True, key="fur_editor")
            
            if st.button("✅ Assign", use_container_width=True, key="fur_assign_btn"):
                count = 0
                for _, row in edited_df.iterrows():
                    if row.get('Allocate'):
                        adm = str(row.get(adm_col, ''))
                        chair_no = f"{chair_prefix}{row.get('Chair No', '')}" if row.get('Chair No') else ""
                        locker_no = f"{locker_prefix}{row.get('Locker No', '')}" if row.get('Locker No') else ""
                        
                        if chair_no and check_duplicate_assignment(school_name, adm, 'chair', chair_no):
                            st.warning(f"⚠️ {row.get(name_col, '')} already has chair {chair_no}!")
                            continue
                        if locker_no and check_duplicate_assignment(school_name, adm, 'locker', locker_no):
                            st.warning(f"⚠️ {row.get(name_col, '')} already has locker {locker_no}!")
                            continue
                        
                        furniture.append({
                            "name": str(row.get(name_col, '')),
                            "adm": adm,
                            "chair": chair_no,
                            "locker": locker_no,
                            "date": alloc_date.strftime('%Y-%m-%d'),
                            "returned": False,
                            "id": generate_code("FUR")
                        })
                        count = count + 1
                
                if count > 0:
                    save_data(f"furniture_{school_name}.json", furniture)
                    add_audit_entry('Furniture Allocated', f"{count} items to {selected_class}")
                    st.success(f"Allocated {count} items!")
                    if 'fur_students' in st.session_state:
                        del st.session_state.fur_students
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_returns():
    school_name = st.session_state.school['name']
    
    st.markdown('<div class="glass-card"><h2>↩️ Return Items</h2>', unsafe_allow_html=True)
    
    search = st.text_input("Search...", placeholder="Search by name, ADM, or item number", key="ret_search_input")
    
    if st.button("🔍 Search", use_container_width=True, key="ret_search_btn"):
        borrowed = load_data(f"borrowed_{school_name}.json", [])
        furniture = load_data(f"furniture_{school_name}.json", [])
        
        active_books = [b for b in borrowed if not b.get('returned') and (
            search.lower() in str(b.get('name', '')).lower() or 
            search in str(b.get('adm', '')) or 
            search in str(b.get('bookNo', ''))
        )]
        
        active_furniture = [f for f in furniture if not f.get('returned') and (
            search.lower() in str(f.get('name', '')).lower() or 
            search in str(f.get('adm', '')) or 
            search in str(f.get('chair', '')) or 
            search in str(f.get('locker', ''))
        )]
        
        st.markdown("### 📚 Books")
        if active_books:
            for item in active_books:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{item.get('name', '')}** - {item.get('bookTitle', '')} (#{item.get('bookNo', '')})")
                with col2:
                    st.write(f"Due: {item.get('returnDate', '')}")
                with col3:
                    if st.button("↩️ Return", key=f"ret_book_{item['id']}"):
                        item['returned'] = True
                        item['actualReturnDate'] = datetime.now().strftime('%Y-%m-%d')
                        books = load_data(f"books_{school_name}.json", [])
                        book = next((b for b in books if b['title'] == item.get('bookTitle', '')), None)
                        if book:
                            book['quantity'] = book.get('quantity', 0) + 1
                        save_data(f"books_{school_name}.json", books)
                        save_data(f"borrowed_{school_name}.json", borrowed)
                        add_audit_entry('Book Returned', f"{item.get('name', '')} returned '{item.get('bookTitle', '')}'")
                        st.success("✅ Book returned!")
                        st.rerun()
                st.divider()
        else:
            st.info("No matching books")
        
        st.markdown("### 🪑 Furniture")
        if active_furniture:
            for item in active_furniture:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{item.get('name', '')}** - Chair: {item.get('chair', '-')}, Locker: {item.get('locker', '-')}")
                with col2:
                    st.write(f"Date: {item.get('date', '')}")
                with col3:
                    if st.button("↩️ Return", key=f"ret_fur_{item['id']}"):
                        item['returned'] = True
                        save_data(f"furniture_{school_name}.json", furniture)
                        add_audit_entry('Furniture Returned', f"{item.get('name', '')} returned items")
                        st.success("✅ Furniture returned!")
                        st.rerun()
                st.divider()
        else:
            st.info("No matching furniture")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_borrowed():
    school_name = st.session_state.school['name']
    borrowed = load_data(f"borrowed_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>📋 Borrowed Books</h2>', unsafe_allow_html=True)
    
    filter_option = st.radio("Filter:", ["📋 All", "✅ Active", "🔴 Overdue"], horizontal=True, key="bor_filter")
    
    today = datetime.now()
    
    if filter_option == "✅ Active":
        filtered = [b for b in borrowed if not b.get('returned')]
    elif filter_option == "🔴 Overdue":
        filtered = [b for b in borrowed if not b.get('returned') and datetime.strptime(b.get('returnDate', '2000-01-01'), '%Y-%m-%d') < today]
    else:
        filtered = borrowed
    
    if filtered:
        st.dataframe(pd.DataFrame(filtered), use_container_width=True)
        if st.button("📎 Export", use_container_width=True, key="bor_export_btn"):
            towrite = BytesIO()
            pd.DataFrame(filtered).to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)
            b64 = base64.b64encode(towrite.read()).decode()
            st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="borrowed.xlsx">📥 Download</a>', unsafe_allow_html=True)
    else:
        st.info("No records")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_members():
    school_name = st.session_state.school['name']
    members = load_data(f"members_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>👥 Members</h2>', unsafe_allow_html=True)
    
    with st.form("frm_member"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name:", placeholder="Member name", key="mem_name")
        with col2:
            mid = st.text_input("ID:", placeholder="Member ID", key="mem_id")
        if st.form_submit_button("➕ Add", use_container_width=True):
            if name:
                members.append({"name": name, "id": mid or generate_code("MEM")})
                save_data(f"members_{school_name}.json", members)
                add_audit_entry('Member Added', name)
                st.success("Added!")
                st.rerun()
    
    search = st.text_input("Search...", placeholder="Search members", key="mem_search")
    filtered = [m for m in members if not search or search.lower() in m['name'].lower() or search in m.get('id', '')]
    
    if filtered:
        for i, m in enumerate(filtered):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{m['name']}** {f'({m["id"]})' if m.get('id') else ''}")
            with col2:
                if st.button("✏️", key=f"edit_mem_{i}"):
                    new_name = st.text_input("Edit name:", m['name'], key=f"edit_name_{i}")
                    if st.button("Save", key=f"save_mem_{i}"):
                        m['name'] = new_name
                        save_data(f"members_{school_name}.json", members)
                        st.rerun()
            with col3:
                if is_admin():
                    if st.button("🗑️", key=f"del_mem_{i}"):
                        members.remove(m)
                        save_data(f"members_{school_name}.json", members)
                        add_audit_entry('Member Removed', m['name'])
                        st.rerun()
            st.divider()
    else:
        st.info("No members found")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_catalog():
    school_name = st.session_state.school['name']
    books = load_data(f"books_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>📚 Catalog</h2>', unsafe_allow_html=True)
    
    with st.form("frm_book"):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            title = st.text_input("Title:", placeholder="Book title", key="cat_title")
        with col2:
            btype = st.selectbox("Type:", ["Textbook", "Novel", "Reference", "Magazine", "Other"], key="cat_type")
        with col3:
            qty = st.number_input("Qty:", 1, 1000, 1, key="cat_qty")
        if st.form_submit_button("📖 Add Book", use_container_width=True):
            if title:
                existing = next((b for b in books if b['title'].lower() == title.lower()), None)
                if existing:
                    existing['quantity'] = existing.get('quantity', 0) + qty
                else:
                    books.append({"title": title, "type": btype, "quantity": qty})
                save_data(f"books_{school_name}.json", books)
                add_audit_entry('Book Added', f"{title} (Qty: {qty})")
                st.success("Book added/updated!")
                st.rerun()
    
    if books:
        for i, b in enumerate(books):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"📖 **{b['title']}**")
            with col2:
                st.write(b.get('type', '-'))
            with col3:
                st.write(f"Qty: {b.get('quantity', 0)}")
            with col4:
                if st.button("🗑️", key=f"del_book_{i}"):
                    add_audit_entry('Book Removed', b['title'])
                    books.pop(i)
                    save_data(f"books_{school_name}.json", books)
                    st.rerun()
            st.divider()
    else:
        st.info("No books in catalog")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_teachers():
    school_name = st.session_state.school['name']
    teachers = load_data(f"teachers_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>👨‍🏫 Teachers</h2>', unsafe_allow_html=True)
    
    if is_admin():
        with st.form("frm_teacher"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                name = st.text_input("Name:", placeholder="Teacher name", key="tea_name")
            with col2:
                subject = st.text_input("Subjects:", placeholder="Subjects", key="tea_subject")
            with col3:
                classes = st.text_input("Classes:", placeholder="Classes", key="tea_classes")
            with col4:
                duty = st.text_input("Class Assigned:", placeholder="Class", key="tea_duty")
            if st.form_submit_button("➕ Add", use_container_width=True):
                if name:
                    teachers.append({"name": name, "subject": subject, "classes": classes, "duty": duty})
                    save_data(f"teachers_{school_name}.json", teachers)
                    add_audit_entry('Teacher Added', name)
                    st.success("Added!")
                    st.rerun()
    
    if teachers:
        for i, t in enumerate(teachers):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.write(f"**{t['name']}**")
            with col2:
                st.write(t.get('subject', '-'))
            with col3:
                st.write(t.get('classes', '-'))
            with col4:
                st.write(t.get('duty', '-'))
            with col5:
                if is_admin():
                    if st.button("🗑️", key=f"del_tea_{i}"):
                        add_audit_entry('Teacher Removed', t['name'])
                        teachers.pop(i)
                        save_data(f"teachers_{school_name}.json", teachers)
                        st.rerun()
            st.divider()
    else:
        st.info("No teachers added")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_classes():
    school_name = st.session_state.school['name']
    classes = load_data(f"classes_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>📋 Class Lists</h2>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader("📥 Import Excel File (.xlsx, .xls)", type=['xlsx', 'xls'], key="cls_upload")
    if uploaded is not None:
        df = pd.read_excel(uploaded)
        st.write("Preview:")
        st.dataframe(df.head(), use_container_width=True)
        
        class_name = st.text_input("Class name:", placeholder="e.g., Grade 4A", key="cls_name_input")
        if st.button("💾 Save", use_container_width=True, key="cls_save_btn"):
            if class_name:
                students = []
                for _, row in df.iterrows():
                    student = {}
                    for col in df.columns:
                        student[col] = str(row[col]) if not pd.isna(row[col]) else ""
                    students.append(student)
                
                classes.append({
                    "name": class_name, "students": students,
                    "created_by": st.session_state.user['name'],
                    "created": datetime.now().strftime("%Y-%m-%d")
                })
                save_data(f"classes_{school_name}.json", classes)
                add_audit_entry('Class Added', f"{class_name} ({len(students)} students)")
                st.success(f"Saved '{class_name}' with {len(students)} students!")
                st.rerun()
    
    if classes:
        for i, cls in enumerate(classes):
            created_info = f"by {cls.get('created_by', 'Unknown')}"
            with st.expander(f"📋 {cls['name']} ({len(cls.get('students', []))} students) - {created_info}"):
                if cls.get('students'):
                    st.dataframe(pd.DataFrame(cls['students']), use_container_width=True)
                if st.button("🗑️ Delete Class", key=f"del_cls_{i}"):
                    add_audit_entry('Class Removed', cls['name'])
                    classes.pop(i)
                    save_data(f"classes_{school_name}.json", classes)
                    st.rerun()
    else:
        st.info("No saved class lists")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_qr():
    st.markdown('<div class="glass-card"><h2>📱 QR Codes</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Generate", "Scan"])
    
    with tab1:
        qr_type = st.selectbox("QR Type:", ["book", "chair", "locker"], key="qr_type_select")
        col1, col2 = st.columns(2)
        with col1:
            start_num = st.number_input("Start Number:", 1, 10000, 1, key="qr_start_num")
        with col2:
            end_num = st.number_input("End Number:", 1, 10000, 10, key="qr_end_num")
        
        if st.button("Generate QR Codes", use_container_width=True, key="qr_gen_btn"):
            cols = st.columns(4)
            for i in range(start_num, min(end_num + 1, start_num + 20)):
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(f"{qr_type}-{i}")
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = BytesIO()
                img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                with cols[(i - start_num) % 4]:
                    st.image(f"data:image/png;base64,{b64}", caption=f"{qr_type}: {i}", width=150)
    
    with tab2:
        st.info("📷 Use your device camera to scan QR codes")
        manual_input = st.text_input("Or enter QR code manually:", placeholder="e.g., book-5", key="qr_manual_input")
        if manual_input:
            st.success(f"✅ Scanned: {manual_input}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_chat():
    school_name = st.session_state.school['name']
    user = st.session_state.user
    users = load_data(f"users_{school_name}.json", [])
    messages = load_data(f"chat_messages_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>💬 Private Chat</h2>', unsafe_allow_html=True)
    
    other_users = [u for u in users if u['email'] != user['email']]
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### 👥 Staff")
        if other_users:
            for u in other_users:
                role_icon = "👑" if u['role'] == 'admin' else "👨‍🏫" if u['role'] == 'teacher' else "📚"
                if st.button(f"{role_icon} {u['name']} ({u['role']})", key=f"chat_user_{u['email']}", use_container_width=True):
                    st.session_state.chat_with = u['email']
        else:
            st.info("No other staff")
    
    with col2:
        if 'chat_with' in st.session_state:
            chat_with = st.session_state.chat_with
            chat_user = next((u for u in users if u['email'] == chat_with), None)
            
            if chat_user:
                can_view = (chat_with == user['email']) or (user['email'] == chat_with) or \
                          (is_admin() and st.session_state.get('show_admin_secret', False))
                
                if can_view or (user['email'] in [chat_with, st.session_state.get('chat_with')]):
                    st.markdown(f"### 💬 Chat with {chat_user['name']}")
                    
                    msgs = [m for m in messages if (m['from'] == user['email'] and m['to'] == chat_with) or 
                           (m['from'] == chat_with and m['to'] == user['email'])]
                    
                    for msg in sorted(msgs, key=lambda x: x['timestamp']):
                        is_mine = msg['from'] == user['email']
                        bg_color = "rgba(233,69,96,0.4)" if is_mine else "rgba(255,255,255,0.1)"
                        align = "flex-end" if is_mine else "flex-start"
                        
                        attachment_html = ""
                        if msg.get('attachment'):
                            att = msg['attachment']
                            if isinstance(att, str):
                                try:
                                    att = json.loads(att)
                                except:
                                    att = {}
                            if att.get('type') == 'image':
                                attachment_html = f'<br><img src="data:{att["mime"]};base64,{att["data"]}" style="max-width:200px;border-radius:8px;margin-top:8px;">'
                            elif att.get('type') == 'file':
                                attachment_html = f'<br>📎 <a href="data:{att["mime"]};base64,{att["data"]}" download="{att["name"]}" style="color:#FFD700;">{att["name"]}</a>'
                            elif att.get('type') == 'voice':
                                attachment_html = f'<br>🎤 Voice note ({att.get("duration", "?")}s)'
                        
                        st.markdown(f"""
                        <div style="display:flex;justify-content:{align};margin:8px 0;">
                            <div style="background:{bg_color};padding:10px 16px;border-radius:16px;max-width:70%;color:#FFF;">
                                <strong>{msg.get('from_name', msg['from'])}:</strong> {msg['message']}
                                {attachment_html}
                                <br><small style="color:rgba(255,255,255,0.5);">{msg['timestamp'][:16]}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # FIXED EMOJI PICKER (persistent selection)
                    with st.expander("😀 Emojis", expanded=False):
                        for category, emojis in EMOJI_CATEGORIES.items():
                            st.markdown(f"**{category}**")
                            cols = st.columns(10)
                            for i, emoji in enumerate(emojis):
                                with cols[i % 10]:
                                    if st.button(emoji, key=f"chat_emoji_btn_{emoji}_{i}"):
                                        st.session_state.selected_emoji = emoji
                    
                    col_a, col_b, col_c = st.columns([5, 1, 1])
                    with col_a:
                        msg_text = st.text_input(
                            "Message", 
                            key="chat_msg_input",
                            placeholder="Type a message...",
                            value=st.session_state.selected_emoji
                        )
                    with col_b:
                        uploaded_file = st.file_uploader("📎", type=['png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt', 'mp3', 'wav'], key="chat_file", label_visibility="collapsed")
                    with col_c:
                        if st.button("📤", use_container_width=True, key="chat_send_btn"):
                            final_msg = msg_text.strip()
                            if final_msg or uploaded_file:
                                msg_data = {
                                    "from": user['email'],
                                    "from_name": user['name'],
                                    "to": chat_with,
                                    "message": final_msg,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "id": generate_code("MSG")
                                }
                                
                                if uploaded_file:
                                    file_bytes = uploaded_file.read()
                                    file_b64 = base64.b64encode(file_bytes).decode()
                                    file_type = "voice" if uploaded_file.type in ['audio/mp3', 'audio/wav'] else "image" if 'image' in uploaded_file.type else "file"
                                    msg_data['attachment'] = {
                                        "name": uploaded_file.name,
                                        "type": file_type,
                                        "mime": uploaded_file.type,
                                        "data": file_b64,
                                        "size": len(file_bytes)
                                    }
                                
                                messages.append(msg_data)
                                save_data(f"chat_messages_{school_name}.json", messages)
                                st.session_state.selected_emoji = ""  # reset after sending
                                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_forum():
    school_name = st.session_state.school['name']
    user = st.session_state.user
    forum_messages = load_data(f"forum_messages_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>📢 Group Forum</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#FFD700;">Messages here are visible to all staff members</p>', unsafe_allow_html=True)
    
    for msg in forum_messages[-50:]:
        role_icon = "👑" if msg.get('role') == 'admin' else "👨‍🏫" if msg.get('role') == 'teacher' else "📚"
        st.markdown(f"""
        <div class="forum-message">
            <strong>{role_icon} {msg.get('from_name', 'Unknown')}</strong>
            <small style="color:rgba(255,255,255,0.5);">({msg.get('timestamp', '')[:16]})</small>
            <br>{msg.get('message', '')}
        </div>
        """, unsafe_allow_html=True)
    
    # Emoji picker (non-persistent, simple approach)
    selected_emoji = None
    with st.expander("😀 Emojis", expanded=False):
        for category, emojis in EMOJI_CATEGORIES.items():
            st.markdown(f"**{category}**")
            cols = st.columns(10)
            for i, emoji in enumerate(emojis):
                with cols[i % 10]:
                    if st.button(emoji, key=f"forum_emoji_{emoji}_{i}"):
                        selected_emoji = emoji
    
    col1, col2 = st.columns([5, 1])
    with col1:
        forum_msg = st.text_area("Message:", key="forum_msg_input", placeholder="Share with everyone...", height=80)
    with col2:
        if st.button("📢 Post", use_container_width=True, key="forum_post_btn"):
            final_msg = forum_msg + (f" {selected_emoji}" if selected_emoji else "")
            if final_msg:
                forum_messages.append({
                    "from": user['email'],
                    "from_name": user['name'],
                    "role": user['role'],
                    "message": final_msg,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "id": generate_code("FRM")
                })
                save_data(f"forum_messages_{school_name}.json", forum_messages)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_notepad():
    school_name = st.session_state.school['name']
    notepad = load_data(f"notepad_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>📝 Shared Notepad</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#FFD700;">Record extras and notes visible to all staff</p>', unsafe_allow_html=True)
    
    if notepad:
        for i, note in enumerate(notepad[-20:]):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.08);padding:10px;border-radius:8px;margin:5px 0;">
                    <strong>{note.get('author', 'Unknown')}</strong>
                    <small style="color:rgba(255,255,255,0.5);">({note.get('timestamp', '')[:16]})</small>
                    <br>{note.get('content', '')}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if is_admin() or note.get('author') == st.session_state.user['name']:
                    if st.button("🗑️", key=f"del_note_{i}"):
                        notepad.pop(i)
                        save_data(f"notepad_{school_name}.json", notepad)
                        st.rerun()
    
    with st.form("frm_notepad"):
        note_content = st.text_area("New Note:", key="note_content", height=100, placeholder="Write your note here...")
        if st.form_submit_button("📝 Add Note", use_container_width=True):
            if note_content:
                notepad.append({
                    "author": st.session_state.user['name'],
                    "content": note_content,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "id": generate_code("NOTE")
                })
                save_data(f"notepad_{school_name}.json", notepad)
                st.success("Note added!")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_system_overview():
    school_name = st.session_state.school['name']
    books = load_data(f"books_{school_name}.json", [])
    borrowed = load_data(f"borrowed_{school_name}.json", [])
    members = load_data(f"members_{school_name}.json", [])
    teachers = load_data(f"teachers_{school_name}.json", [])
    furniture = load_data(f"furniture_{school_name}.json", [])
    users = load_data(f"users_{school_name}.json", [])
    classes = load_data(f"classes_{school_name}.json", [])
    messages = load_data(f"chat_messages_{school_name}.json", [])
    forum = load_data(f"forum_messages_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>🔍 System Overview</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-card"><strong>🏫 School</strong><br>{school_name}<br>Code: {st.session_state.school["invite_code"]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><strong>📚 Books</strong><br>Total: {sum(b.get("quantity",0) for b in books)}<br>Active: {len([b for b in borrowed if not b.get("returned")])}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><strong>👥 People</strong><br>Staff: {len(users)}<br>Members: {len(members)}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_audit_log():
    school_name = st.session_state.school['name']
    audit_log = load_data(f"audit_log_{school_name}.json", [])
    
    st.markdown('<div class="glass-card"><h2>📝 Audit Log</h2>', unsafe_allow_html=True)
    
    if not is_admin():
        st.warning("Only administrators can view the audit log.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    if audit_log:
        st.dataframe(pd.DataFrame(list(reversed(audit_log[-100:]))), use_container_width=True)
        if st.button("📎 Export", use_container_width=True, key="log_export_btn"):
            towrite = BytesIO()
            pd.DataFrame(audit_log).to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)
            b64 = base64.b64encode(towrite.read()).decode()
            st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="audit_log.xlsx">📥 Download</a>', unsafe_allow_html=True)
    else:
        st.info("No audit log entries")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_reports():
    school_name = st.session_state.school['name']
    
    st.markdown('<div class="glass-card"><h2>📈 Reports & Analytics</h2>', unsafe_allow_html=True)
    
    report_type = st.selectbox("Report Type:", ["Books Overview", "Furniture Overview", "Overdue Analysis", "Complete Dashboard"], key="rep_type_select")
    
    if st.button("📊 Generate Report", use_container_width=True, key="rep_gen_btn"):
        if report_type == "Books Overview":
            borrowed = load_data(f"borrowed_{school_name}.json", [])
            if borrowed:
                df = pd.DataFrame(borrowed)
                st.dataframe(df, use_container_width=True)
                
                status_counts = df['returned'].value_counts()
                fig = px.bar(x=['Active', 'Returned'], y=[status_counts.get(False, 0), status_counts.get(True, 0)],
                            title="Books by Status", color_discrete_sequence=['#e94560', '#28a745'])
                st.plotly_chart(fig, use_container_width=True)
        
        elif report_type == "Furniture Overview":
            furniture = load_data(f"furniture_{school_name}.json", [])
            if furniture:
                df = pd.DataFrame(furniture)
                st.dataframe(df, use_container_width=True)
                
                status_counts = df['returned'].value_counts()
                fig = px.pie(values=[status_counts.get(False, 0), status_counts.get(True, 0)],
                            names=['Active', 'Returned'], title="Furniture Status",
                            color_discrete_sequence=['#e94560', '#28a745'])
                st.plotly_chart(fig, use_container_width=True)
        
        elif report_type == "Overdue Analysis":
            borrowed = load_data(f"borrowed_{school_name}.json", [])
            today = datetime.now()
            overdue = [b for b in borrowed if not b.get('returned') and datetime.strptime(b.get('returnDate', '2000-01-01'), '%Y-%m-%d') < today]
            if overdue:
                df = pd.DataFrame(overdue)
                st.dataframe(df, use_container_width=True)
                st.metric("🔴 Overdue Books", len(overdue))
            else:
                st.success("No overdue books!")
        
        elif report_type == "Complete Dashboard":
            books = load_data(f"books_{school_name}.json", [])
            borrowed = load_data(f"borrowed_{school_name}.json", [])
            members = load_data(f"members_{school_name}.json", [])
            teachers = load_data(f"teachers_{school_name}.json", [])
            furniture = load_data(f"furniture_{school_name}.json", [])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📚 Total Books", sum(b.get('quantity', 0) for b in books))
            with col2:
                st.metric("📖 Active Loans", len([b for b in borrowed if not b.get('returned')]))
            with col3:
                st.metric("👥 Members", len(members))
            with col4:
                st.metric("👨‍🏫 Teachers", len(teachers))
            
            total = sum(b.get('quantity', 0) for b in books)
            active = len([b for b in borrowed if not b.get('returned')])
            fig = px.pie(values=[active, total - active], names=['Borrowed', 'Available'],
                        title="Book Distribution", color_discrete_sequence=['#e94560', '#28a745'])
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_settings():
    school_name = st.session_state.school['name']
    
    st.markdown('<div class="glass-card"><h2>⚙️ Settings</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 Theme", "💾 Data", "👥 Staff"])
    
    with tab1:
        st.markdown("### 🎨 Wallpapers (100+)")
        wallpaper = st.selectbox("Choose Wallpaper:", list(WALLPAPERS.keys()), index=list(WALLPAPERS.keys()).index(st.session_state.wallpaper), key="set_wallpaper")
        if st.button("Apply Theme", use_container_width=True, key="set_apply_theme"):
            st.session_state.wallpaper = wallpaper
            st.rerun()
        if wallpaper != "None":
            st.image(WALLPAPERS[wallpaper], width=400, caption=wallpaper)
    
    with tab2:
        st.markdown("### 💾 Data Management")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Backup", use_container_width=True, key="set_backup_btn"):
                all_data = {}
                for f in ["books", "members", "borrowed", "teachers", "classes", "furniture", "audit_log", "chat_messages", "forum_messages", "notepad"]:
                    all_data[f] = load_data(f"{f}_{school_name}.json", [])
                b64 = base64.b64encode(json.dumps(all_data, indent=2).encode()).decode()
                st.markdown(f'<a href="data:application/json;base64,{b64}" download="srms_backup.json">📥 Download</a>', unsafe_allow_html=True)
        with col2:
            uploaded_file = st.file_uploader("📤 Restore", type=['json'], key="set_restore_upload")
            if uploaded_file and st.button("Restore", use_container_width=True, key="set_restore_btn"):
                try:
                    data = json.load(uploaded_file)
                    for f, fd in data.items():
                        save_data(f"{f}_{school_name}.json", fd)
                    st.success("Restored!")
                    st.rerun()
                except:
                    st.error("Invalid file!")
        with col3:
            if is_admin():
                if st.button("⚠️ Clear All", use_container_width=True, key="set_clear_btn"):
                    if st.text_input("Type DELETE:", key="set_del") == "DELETE":
                        for f in ["books", "members", "borrowed", "teachers", "classes", "furniture", "audit_log", "chat_messages", "forum_messages", "notepad"]:
                            save_data(f"{f}_{school_name}.json", [])
                        st.error("Cleared!")
                        st.rerun()
    
    with tab3:
        st.markdown("### 👥 Staff Management")
        
        if is_admin():
            with st.form("frm_staff_settings"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    email = st.text_input("Email:", placeholder="staff@school.edu", key="set_staff_email")
                with col2:
                    name = st.text_input("Name:", placeholder="Staff name", key="set_staff_name")
                with col3:
                    role = st.selectbox("Role:", ["teacher", "librarian", "admin"], key="set_staff_role")
                with col4:
                    password = st.text_input("Password:", placeholder="Auto if empty", key="set_staff_password")
                
                if st.form_submit_button("➕ Create Staff", use_container_width=True):
                    if email and name:
                        users = load_data(f"users_{school_name}.json", [])
                        if any(u['email'] == email for u in users):
                            st.error("Email exists!")
                        else:
                            gen_pw = password if password else generate_code("", 8)
                            users.append({
                                "name": name, "email": email, "role": role,
                                "code": st.session_state.school['invite_code'],
                                "password": hash_password(gen_pw),
                                "staff_id": f"{role.upper()}-{generate_code('', 4)}",
                                "joined": datetime.now().strftime("%Y-%m-%d"), "phone": ""
                            })
                            save_data(f"users_{school_name}.json", users)
                            add_audit_entry('Staff Created', f"{name} as {role}")
                            st.success(f"Created {role}: {name}" + (f" (PW: {gen_pw})" if not password else ""))
                            st.rerun()
        
        users = load_data(f"users_{school_name}.json", [])
        st.markdown("#### Current Staff")
        
        for i, u in enumerate(users):
            role_icon = "👑" if u['role'] == 'admin' else "👨‍🏫" if u['role'] == 'teacher' else "📚"
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.write(f"{role_icon} **{u['name']}** - {u['role'].upper()}")
            with col2:
                st.write(f"📧 {u.get('email', '')}")
            with col3:
                st.write(f"ID: {u.get('staff_id', '')}")
            with col4:
                if is_admin() and u['email'] != st.session_state.user['email'] and u['role'] != 'admin':
                    if st.button("👑 Promote", key=f"promote_{i}"):
                        u['role'] = 'admin'
                        save_data(f"users_{school_name}.json", users)
                        add_audit_entry('Staff Promoted', f"{u['name']} promoted to admin")
                        st.success(f"{u['name']} is now admin!")
                        st.rerun()
            with col5:
                if is_admin() and u['email'] != st.session_state.user['email']:
                    admin_count = len([x for x in users if x['role'] == 'admin'])
                    if u['role'] != 'admin' or admin_count > 1:
                        if st.button("🗑️", key=f"del_staff_{i}"):
                            add_audit_entry('Staff Removed', f"{u['name']}")
                            users.pop(i)
                            save_data(f"users_{school_name}.json", users)
                            st.rerun()
            st.divider()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============== MAIN ==============
def main():
    if st.session_state.page == 'startup':
        startup_page()
    elif st.session_state.page == 'dashboard':
        dashboard_page()

if __name__ == "__main__":
    main()
