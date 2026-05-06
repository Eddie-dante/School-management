# app.py - SRMS - School Resource Management System by WeGEM
# Integrated with Supabase (no JSON files)
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
from supabase import create_client, Client

# ============ Supabase Configuration ============
SUPABASE_URL = "https://mcjkdnhbbnxvvgnjbuzy.supabase.co"
SUPABASE_SECRET = "sb_secret_o1cZAZTjzwpFJxwXswr5ig_IGPU3uh3"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET)

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
    "attachments": "chat_messages"
}

def load_data(filename, default=None):
    """Load data from Supabase."""
    try:
        base = filename.rsplit(".json", 1)[0]
        if "_" in base:
            data_type, school = base.rsplit("_", 1)
        else:
            data_type, school = base, None

        if data_type in TABLE_MAP:
            table = TABLE_MAP[data_type]
            if school:
                resp = supabase.table(table).select("*").eq("school_name", school).execute()
            else:
                resp = supabase.table(table).select("*").execute()
            return resp.data if resp.data else (default if default is not None else [])
        elif filename == "schools.json":
            resp = supabase.table("schools").select("*").execute()
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
    """Save data to Supabase."""
    try:
        base = filename.rsplit(".json", 1)[0]
        if "_" in base:
            data_type, school = base.rsplit("_", 1)
        else:
            data_type, school = base, None

        if data_type in TABLE_MAP:
            table = TABLE_MAP[data_type]
            if school:
                supabase.table(table).delete().eq("school_name", school).execute()
                if isinstance(data, list) and data:
                    for item in data:
                        item['school_name'] = school
                    supabase.table(table).insert(data).execute()
        elif filename == "schools.json":
            for sname, sdata in data.items():
                sdata['name'] = sname
                supabase.table("schools").upsert(sdata, on_conflict="name").execute()
    except Exception as e:
        st.error(f"Database write error ({filename}): {e}")

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
    "Library": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1920",
    "Classroom": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=1920",
    "School Building": "https://images.unsplash.com/photo-1577896851231-70ef18881754?w=1920",
    "Study Desk": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1920",
    "Bookshelf": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1920",
    "Graduation": "https://images.unsplash.com/photo-1523050854058-8df90910f68e?w=1920",
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
    "City Lights": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1920",
    "Neon City": "https://images.unsplash.com/photo-1557682257-2f9c97a8a469?w=1920",
    "Bridge Night": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1920",
    "Modern Building": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=1920",
    "Tokyo Street": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1920",
    "New York": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=1920",
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
    "Anime Sunset": "https://images.unsplash.com/photo-1578632767115-351597cf1bfe?w=1920",
    "Anime Sky": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1920",
    "Anime City": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1920",
    "Anime Garden": "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=1920",
    "Anime Night": "https://images.unsplash.com/photo-1557682257-2f9c97a8a469?w=1920",
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

EMOJI_CATEGORIES = {
    "😀 Smileys": ["😀","😃","😄","😁","😅","😂","🤣","😊","😇","🙂","😉","😌","😍","🥰","😘","😗","😋","😛","😜","🤪","😝","🤑","🤗","🤭","🤫","🤔","🤐","🤨","😐","😑","😶","😏","😒","🙄","😬","😮","😯","😲","😳","🥺","😢","😭","😤","😡","🤬","😈","👿","💀","☠️"],
    "👍 Gestures": ["👍","👎","👌","✌️","🤞","🤟","🤘","🤙","👈","👉","👆","👇","☝️","✋","🤚","🖐️","🖖","👋","🤏","✍️","👏","🙌","🫶","🤝","🙏"],
    "❤️ Hearts": ["❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎","💔","❣️","💕","💞","💓","💗","💖","💘","💝","💟"],
    "📚 School": ["📚","📖","📝","✏️","🖊️","📏","📐","🎓","🏫","📋","📎","🖇️","🗂️","📁","📌","📍","✂️","🖍️"],
    "🎯 Objects": ["🎯","⭐","🌟","✨","🔥","💯","✅","❌","⚠️","🔔","🔕","📢","📣","💡","🔦","💰","🎁","🏆","🥇","🥈","🥉","📅","⏰","🔑","🔒","🔓"],
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
        .stButton button {{ background: linear-gradient(135deg, #e94560, #c62a47) !important; border: none !important; border-radius: 10px !important; color: white !important; font-weight: 600 !important; padding: 10px 20px !important; }}
        .glass-card {{ background: rgba(255,255,255,0.12) !important; backdrop-filter: blur(20px) !important; border-radius: 16px !important; padding: 25px !important; margin: 15px 0 !important; border: 1px solid rgba(212,175,55,0.25) !important; }}
        .stat-card {{ background: rgba(255,255,255,0.08) !important; backdrop-filter: blur(15px) !important; padding: 25px !important; border-radius: 16px !important; border-left: 4px solid #e94560 !important; text-align: center !important; margin: 8px 0 !important; }}
        .stat-value {{ font-size: 2.5em !important; font-weight: 900 !important; color: #FFFFFF !important; }}
        .stat-label {{ color: rgba(255,255,255,0.75) !important; font-size: 0.9em !important; }}
        .school-code-banner {{ background: rgba(255,255,255,0.1) !important; backdrop-filter: blur(15px) !important; border: 2px dashed rgba(233,69,96,0.4) !important; border-radius: 16px !important; padding: 25px !important; text-align: center !important; }}
        .invite-code {{ font-family: 'Courier New', monospace !important; font-size: 2.5em !important; font-weight: 800 !important; letter-spacing: 8px !important; color: #FFFFFF !important; }}
    </style>
    """

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
        <div style="font-size: 55px; font-weight: 900; color: #0a0e27;">SRMS</div>
        <h1 style="font-size: 3.5em; background: linear-gradient(180deg, #f0d060, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SRMS</h1>
        <p style="font-size: 1.4em; color: #FFFFFF;">School Resource Management System</p>
        <p style="color: #d4af37;">by <span style="color: #f0d060; font-weight: 700;">WeGEM</span> (Edwin)</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔑 Staff Login", use_container_width=True):
            st.session_state.action = 'login'
    with col2:
        if st.button("📝 Staff Sign Up", use_container_width=True):
            st.session_state.action = 'signup'
    with col3:
        if st.button("🏫 Create School", use_container_width=True):
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
    st.markdown('<h3>🔐 Staff Login</h3>', unsafe_allow_html=True)
    with st.form("frm_login"):
        name = st.text_input("👤 Your Full Name")
        school_name = st.text_input("🏢 School Name")
        invite_code = st.text_input("🔑 Invite Code")
        password = st.text_input("🔒 Password", type="password")
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
    st.markdown('<h3>📝 Staff Sign Up</h3>', unsafe_allow_html=True)
    with st.form("frm_signup"):
        name = st.text_input("👤 Full Name")
        email = st.text_input("📧 Email")
        phone = st.text_input("📞 Phone")
        school_name = st.text_input("🏢 School Name")
        invite_code = st.text_input("🔑 Invite Code")
        staff_id = st.text_input("👤 Staff ID (Optional)")
        password = st.text_input("🔒 Create Password", type="password")
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
    st.markdown('<h3>🏫 Create New School</h3>', unsafe_allow_html=True)
    with st.form("frm_create"):
        school_name = st.text_input("🏢 School Name")
        address = st.text_input("📍 School Address")
        admin_name = st.text_input("👤 Admin Full Name")
        admin_email = st.text_input("📧 Admin Email")
        admin_phone = st.text_input("📞 Admin Phone")
        password = st.text_input("🔒 Password", type="password")
        confirm = st.text_input("🔒 Confirm Password", type="password")
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
        <h1>🏫 {school_name}</h1>
        <p>{user['name']} <span style="background:{'#e94560' if user['role']=='admin' else '#0f3460'};color:#FFF;padding:4px 12px;border-radius:20px;">{user['role'].upper()}</span></p>
    </div>
    """, unsafe_allow_html=True)
    if is_admin():
        st.markdown(f"""
        <div class="school-code-banner">
            <p>🏫 School Invite Code</p>
            <div class="invite-code">{st.session_state.school['invite_code']}</div>
        </div>
        """, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:15px;background:rgba(255,255,255,0.08);border-radius:12px;margin-bottom:15px;">
            <div style="width:50px;height:50px;background:linear-gradient(135deg,#d4af37,#f0d060);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;color:#0a0e27;">{user['name'][0].upper()}</div>
            <p style="color:#FFFFFF;font-weight:700;">{user['name']}</p>
            <p style="color:#d4af37;font-size:0.8em;">{user['role'].upper()}</p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("🎨 Theme", expanded=False):
            wallpaper = st.selectbox("Wallpaper", list(WALLPAPERS.keys()), index=list(WALLPAPERS.keys()).index(st.session_state.wallpaper))
            if wallpaper != st.session_state.wallpaper:
                st.session_state.wallpaper = wallpaper
                st.rerun()
        st.markdown("---")
        with st.expander("📊 MAIN", expanded=True):
            if st.button("📊 Dashboard"): st.session_state.current_section = 'dashboard'; st.rerun()
        with st.expander("📖 LIBRARY", expanded=False):
            if st.button("📖 Book Issuing"): st.session_state.current_section = 'bookIssuing'; st.rerun()
            if st.button("👤 Lend Book"): st.session_state.current_section = 'individualLending'; st.rerun()
            if st.button("↩️ Returns"): st.session_state.current_section = 'return'; st.rerun()
            if st.button("📋 Borrowed"): st.session_state.current_section = 'borrowedLog'; st.rerun()
            if st.button("📚 Catalog"): st.session_state.current_section = 'bookCatalog'; st.rerun()
        with st.expander("🪑 RESOURCES", expanded=False):
            if st.button("🪑 Furniture"): st.session_state.current_section = 'furnitureAllocation'; st.rerun()
            if st.button("📱 QR Codes"): st.session_state.current_section = 'qr'; st.rerun()
        with st.expander("👥 PEOPLE", expanded=False):
            if st.button("👥 Members"): st.session_state.current_section = 'memberManagement'; st.rerun()
            if st.button("👨‍🏫 Teachers"): st.session_state.current_section = 'teacherAllocation'; st.rerun()
            if st.button("📋 Classes"): st.session_state.current_section = 'classListManager'; st.rerun()
        with st.expander("💬 COMMUNICATION", expanded=False):
            if st.button("💬 Private Chat"): st.session_state.current_section = 'chat'; st.rerun()
            if st.button("📢 Group Forum"): st.session_state.current_section = 'forum'; st.rerun()
            if st.button("📝 Notepad"): st.session_state.current_section = 'notepad'; st.rerun()
        with st.expander("📈 TOOLS", expanded=False):
            if st.button("🔍 Overview"): st.session_state.current_section = 'systemOverview'; st.rerun()
            if st.button("📝 Log"): st.session_state.current_section = 'auditLog'; st.rerun()
            if st.button("📈 Reports"): st.session_state.current_section = 'reports'; st.rerun()
        with st.expander("⚙️ SYSTEM", expanded=False):
            if st.button("⚙️ Settings"): st.session_state.current_section = 'settings'; st.rerun()
        if is_admin():
            st.markdown("---")
            with st.expander("🔐 Admin Secret", expanded=False):
                secret_input = st.text_input("Enter key combo:", type="password")
                if secret_input == "EGM" and st.button("🔓 Unlock Private Chats"):
                    st.session_state.show_admin_secret = True
                    st.success("🔓 Admin can now view all private chats!")
                    st.rerun()
        if st.button("🚪 Logout", type="primary"):
            add_audit_entry('Logout', user['name'])
            st.session_state.user = None
            st.session_state.school = None
            st.session_state.page = 'startup'
            st.rerun()
        st.markdown('<p style="color:rgba(255,255,255,0.4);font-size:0.7em;text-align:center;">SRMS v6.0 | by WeGEM (Edwin) | © 2025</p>', unsafe_allow_html=True)

    section = st.session_state.current_section
    if section == 'dashboard': render_dashboard()
    elif section == 'bookIssuing': render_book_issuing()
    elif section == 'individualLending': render_individual_lending()
    elif section == 'furnitureAllocation': render_furniture()
    elif section == 'return': render_returns()
    elif section == 'borrowedLog': render_borrowed()
    elif section == 'memberManagement': render_members()
    elif section == 'bookCatalog': render_catalog()
    elif section == 'teacherAllocation': render_teachers()
    elif section == 'classListManager': render_classes()
    elif section == 'qr': render_qr()
    elif section == 'chat': render_chat()
    elif section == 'forum': render_forum()
    elif section == 'notepad': render_notepad()
    elif section == 'systemOverview': render_system_overview()
    elif section == 'auditLog': render_audit_log()
    elif section == 'reports': render_reports()
    elif section == 'settings': render_settings()

# ============ RENDER FUNCTIONS (abbreviated for space, but full code from previous response is identical) ============
# ... [include all render_* functions as in previous full code, unchanged except for chat fix below]

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
        for u in other_users:
            role_icon = "👑" if u['role'] == 'admin' else "👨‍🏫" if u['role'] == 'teacher' else "📚"
            if st.button(f"{role_icon} {u['name']} ({u['role']})", key=f"chat_user_{u['email']}"):
                st.session_state.chat_with = u['email']

    with col2:
        if 'chat_with' in st.session_state:
            chat_with = st.session_state.chat_with
            chat_user = next((u for u in users if u['email'] == chat_with), None)
            if chat_user:
                can_view = (chat_with == user['email']) or (user['email'] == chat_with) or \
                          (is_admin() and st.session_state.get('show_admin_secret', False))
                if can_view:
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
                                att = json.loads(att)
                            if att.get('type') == 'image':
                                attachment_html = f'<br><img src="data:{att["mime"]};base64,{att["data"]}" style="max-width:200px;border-radius:8px;">'
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

                    # Emoji picker (fixed)
                    with st.expander("😀 Emojis", expanded=False):
                        for category, emojis in EMOJI_CATEGORIES.items():
                            st.markdown(f"**{category}**")
                            cols = st.columns(10)
                            for i, emoji in enumerate(emojis):
                                with cols[i % 10]:
                                    if st.button(emoji, key=f"emoji_{emoji}_{i}"):
                                        st.session_state.selected_emoji = emoji

                    col_a, col_b, col_c = st.columns([5, 1, 1])
                    with col_a:
                        msg_text = st.text_input("Message", key="chat_msg_input",
                                                 placeholder="Type a message...",
                                                 value=st.session_state.selected_emoji)
                    with col_b:
                        uploaded_file = st.file_uploader("📎", type=['png','jpg','jpeg','gif','pdf','docx','txt','mp3','wav'],
                                                         key="chat_file", label_visibility="collapsed")
                    with col_c:
                        if st.button("📤", key="chat_send_btn"):
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
                                    file_type = "voice" if uploaded_file.type in ['audio/mp3','audio/wav'] else "image" if 'image' in uploaded_file.type else "file"
                                    msg_data['attachment'] = {
                                        "name": uploaded_file.name,
                                        "type": file_type,
                                        "mime": uploaded_file.type,
                                        "data": file_b64,
                                        "size": len(file_bytes)
                                    }
                                messages.append(msg_data)
                                save_data(f"chat_messages_{school_name}.json", messages)
                                st.session_state.selected_emoji = ""
                                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ... (include all other render functions exactly as in previous full code, they are unchanged)

# ============== MAIN ==============
def main():
    if st.session_state.page == 'startup':
        startup_page()
    elif st.session_state.page == 'dashboard':
        dashboard_page()

if __name__ == "__main__":
    main()
