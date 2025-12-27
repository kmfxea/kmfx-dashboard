# ==================== KMFX EA DASHBOARD - PROFESSIONAL RESPONSIVE FINAL ====================

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import sqlite3
import datetime
import bcrypt
import os
import plotly.express as px
# ------------------------- KEEP-ALIVE FOR STREAMLIT CLOUD -------------------------
def keep_alive():
    while True:
        try:
            requests.get("https://kmfx-dashboard.streamlit.app", timeout=10)  # Palitan mo 'to ng actual URL mo
        except:
            pass
        time.sleep(1500)  # Every 25 minutes (1500 seconds)

# Only run in production (Streamlit Cloud)
if os.getenv("STREAMLIT_SHARING", False) or st.secrets.get("KEEP_ALIVE", False):
    if not hasattr(st, "_keep_alive_thread_started"):
        thread = threading.Thread(target=keep_alive, daemon=True)
        thread.start()
        st._keep_alive_thread_started = True
# ------------------------- PAGE CONFIG -------------------------
st.set_page_config(
    page_title="KMFX Dashboard",
    layout="wide",  # Uses full width but with responsive padding
    initial_sidebar_state="collapsed"
)
# ------------------------- GOOGLE FONTS (AMAZING PREMIUM FONTS) -------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Cinzel:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)
# ------------------------- THEME & COLORS (DEFINE ONCE, USE EVERYWHERE) -------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Define accent color globally (safe for all pages)
accent = "#3b82f6" if st.session_state.theme == "dark" else "#2563eb"
surface_color = "rgba(15, 25, 50, 0.6)" if st.session_state.theme == "dark" else "rgba(255, 255, 255, 0.7)"
border_color = "rgba(59, 130, 246, 0.3)" if st.session_state.theme == "dark" else "rgba(0, 0, 0, 0.1)"
text_secondary = "#94a3b8"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {"#0f172a" if st.session_state.theme == "dark" else "#f8fafc"};
        color: {"#e2e8f0" if st.session_state.theme == "dark" else "#1e293b"};
    }}
    /* Other styles... */
</style>
""", unsafe_allow_html=True)

# ------------------------- DARK/LIGHT MODE -------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if st.session_state.theme == "dark":
    bg_color = "#0f172a"
    surface_color = "rgba(30, 41, 59, 0.6)"  # Semi-transparent slate
    text_color = "#e2e8f0"
    accent_color = "#3b82f6"
    border_color = "rgba(148, 163, 184, 0.3)"
else:
    bg_color = "#f8fafc"
    surface_color = "rgba(255, 255, 255, 0.7)"
    text_color = "#1e293b"
    accent_color = "#2563eb"
    border_color = "rgba(0, 0, 0, 0.1)"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        padding: 1rem;
    }}
    /* Menu container - subtle transparent card */
    .menu-container {{
        background: {surface_color};
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 2rem;
        border: 1px solid {border_color};
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    /* Responsive menu items - wrap on small screens */
    .css-1v0mbdj {{  /* Streamlit option_menu nav links */
        flex-wrap: wrap !important;
        justify-content: center !important;
    }}
    .nav-link {{
        font-size: 15px !important;
        padding: 10px 14px !important;
        margin: 4px !important;
        border-radius: 12px !important;
    }}
    .nav-link-selected {{
        background-color: {accent_color} !important;
        color: white !important;
        font-weight: 600 !important;
    }}
    /* Content cards */
    .content-card {{
        background: {surface_color};
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid {border_color};
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }}
    h1, h2, h3 {{
        color: {text_color};
    }}
    .stButton > button {{
        border-radius: 12px;
        height: 3em;
        width: 100%;
    }}
    /* Mobile optimizations */
    @media (max-width: 768px) {{
        .menu-container {{ padding: 8px; }}
        .nav-link {{ font-size: 14px !important; padding: 8px 12px !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# ------------------------- DATABASE SETUP (FULLY FIXED - NO ERRORS EVER) -------------------------
conn = sqlite3.connect('kmfx_ultimate.db', check_same_thread=False)
c = conn.cursor()

# === SAFE COLUMN ADDITION ===
def add_column_if_not_exists(table, column, definition):
    try:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Already exists

# === MIGRATIONS ===
add_column_if_not_exists("clients", "current_equity", "REAL DEFAULT 0")
add_column_if_not_exists("clients", "withdrawable_balance", "REAL DEFAULT 0")
add_column_if_not_exists("clients", "referred_by", "INTEGER")
add_column_if_not_exists("clients", "address", "TEXT")
add_column_if_not_exists("clients", "mobile_number", "TEXT")
add_column_if_not_exists("clients", "referral_code", "TEXT UNIQUE")
add_column_if_not_exists("notifications", "read", "INTEGER DEFAULT 0")
add_column_if_not_exists("announcements", "likes", "INTEGER DEFAULT 0")

# === SAFE TABLE CREATION ===
tables = [
    '''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT DEFAULT 'Regular',
        accounts TEXT,
        expiry TEXT,
        start_balance REAL DEFAULT 0,
        current_equity REAL DEFAULT 0,
        withdrawable_balance REAL DEFAULT 0,
        add_date TEXT,
        referred_by INTEGER,
        referral_code TEXT UNIQUE,
        notes TEXT,
        address TEXT,
        mobile_number TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS users (
        client_id INTEGER UNIQUE,
        username TEXT UNIQUE,
        password TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        name TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS profits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        profit REAL,
        date TEXT,
        client_share REAL,
        your_share REAL,
        referral_bonus REAL DEFAULT 0
    )''',
    '''CREATE TABLE IF NOT EXISTS client_licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        key TEXT,
        enc_data TEXT,
        version TEXT,
        date_generated TEXT,
        expiry TEXT,
        allow_live INTEGER DEFAULT 1
    )''',
    '''CREATE TABLE IF NOT EXISTS client_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        file_name TEXT,
        original_name TEXT,
        upload_date TEXT,
        sent_by TEXT,
        notes TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        date TEXT,
        posted_by TEXT,
        likes INTEGER DEFAULT 0
    )''',
    '''CREATE TABLE IF NOT EXISTS announcement_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER,
        file_name TEXT,
        original_name TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_client_id INTEGER DEFAULT NULL,
        from_admin TEXT DEFAULT NULL,
        to_client_id INTEGER DEFAULT NULL,
        message TEXT,
        timestamp TEXT,
        read INTEGER DEFAULT 0
    )''',
    '''CREATE TABLE IF NOT EXISTS message_attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER,
        file_name TEXT,
        original_name TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        title TEXT,
        message TEXT,
        category TEXT DEFAULT 'General',
        date TEXT,
        read INTEGER DEFAULT 0
    )''',
    '''CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        amount REAL,
        method TEXT,
        details TEXT,
        status TEXT DEFAULT 'Pending',
        date_requested TEXT,
        date_processed TEXT DEFAULT NULL,
        processed_by TEXT DEFAULT NULL,
        notes TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS ea_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version TEXT,
        file_name TEXT,
        upload_date TEXT,
        notes TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS announcement_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER,
        commenter_name TEXT,
        comment TEXT,
        timestamp TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        action TEXT,
        details TEXT,
        user_type TEXT,
        user_id INTEGER DEFAULT NULL
    )'''
]

for sql in tables:
    c.execute(sql)
conn.commit()

# === CREATE FOLDERS ===
for folder in [
    "uploaded_files",
    "uploaded_files/messages",
    "uploaded_files/client_files",
    "uploaded_files/announcements"
]:
    os.makedirs(folder, exist_ok=True)

# ------------------------- HELPERS -------------------------
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode('utf-8'), hashed.encode('utf-8'))

def add_log(action, details="", user_type="System", user_id=None):
    try:
        c.execute("INSERT INTO logs (timestamp, action, details, user_type, user_id) VALUES (?, ?, ?, ?, ?)",
                  (datetime.datetime.now().isoformat(), action, details, user_type, user_id))
        conn.commit()
    except Exception as e:
        print(f"Log error: {e}")

# === CACHED LOADERS (WITH EASY CLEAR FOR REALTIME) ===
@st.cache_data(ttl=600)  # Increased to 10 mins, but we clear manually when needed
def load_clients(_conn=conn):
    df = pd.read_sql("SELECT * FROM clients", _conn)
    numeric_cols = ['start_balance', 'current_equity', 'withdrawable_balance']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

@st.cache_data(ttl=600)
def load_profits_summary(_conn=conn):
    return pd.read_sql("SELECT profit, client_share, your_share, referral_bonus, date, client_id FROM profits", _conn)

@st.cache_data(ttl=600)
def load_withdrawals(_conn=conn):
    return pd.read_sql("SELECT amount, status, date_requested, date_processed FROM withdrawals", _conn)

# Non-cached for logs (always fresh)
def load_recent_logs():
    return pd.read_sql("SELECT action, details, timestamp FROM logs ORDER BY timestamp DESC LIMIT 20", conn)

# === OPTIMIZED REFERRAL CODE (FAST & SAFE) ===
def generate_referral_code(name, client_id):
    base = ''.join(e for e in name.lower().replace(" ", "") if e.isalnum())
    code_base = f"{base}{client_id}"
    
    existing = pd.read_sql(f"SELECT referral_code FROM clients WHERE referral_code LIKE '{code_base}%'", conn)['referral_code'].tolist()
    
    suffixes = []
    for code in existing:
        if code.startswith(code_base):
            suffix = code[len(code_base):]
            if suffix.isdigit():
                suffixes.append(int(suffix))
    
    counter = 1
    while counter in suffixes:
        counter += 1
    
    return code_base if counter == 1 else f"{code_base}{counter}"

# === REFRESH CURRENT CLIENT (CRITICAL FOR REALTIME) ===
def refresh_current_client():
    if st.session_state.get('client_id'):
        try:
            client_data = pd.read_sql(f"SELECT * FROM clients WHERE id = {st.session_state.client_id}", conn)
            if not client_data.empty:
                st.session_state.current_client = client_data.iloc[0].to_dict()
        except Exception as e:
            st.error("Error refreshing profile data. Please re-login.")
            print(f"Refresh client error: {e}")

# === CLEAR ALL CACHES FUNCTION (CALL THIS AFTER MAJOR CHANGES) ===
def clear_all_caches():
    load_clients.clear()
    load_profits_summary.clear()
    load_withdrawals.clear()

# ------------------------- SESSION STATE -------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.is_owner = False
    st.session_state.is_admin = False
    st.session_state.client_id = None
    st.session_state.current_client = None

# ------------------------- LOGIN PAGE -------------------------
if not st.session_state.authenticated:
    st.title("KMFX EA Dashboard")
    st.subheader("Premium Trading Management Portal")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_type = st.radio("Login as", ["Owner", "Admin", "Client"], horizontal=True)

        if login_type == "Owner":
            pw = st.text_input("Owner Master Password", type="password")
            if st.button("LOGIN AS OWNER", type="primary"):
                if pw == "@@Kingminted@@100590":  # Change in production!
                    st.session_state.authenticated = True
                    st.session_state.is_owner = True
                    add_log("Login", "Owner logged in", "Owner")
                    st.success("Welcome, Owner!")
                    st.rerun()
                else:
                    st.error("Incorrect password")

        elif login_type == "Admin":
            username = st.text_input("Admin Username")
            pw = st.text_input("Password", type="password")
            if st.button("LOGIN AS ADMIN", type="primary"):
                row = c.execute("SELECT password FROM admins WHERE username=?", (username,)).fetchone()
                if row and check_password(pw, row[0]):
                    st.session_state.authenticated = True
                    st.session_state.is_admin = True
                    add_log("Login", f"Admin {username} logged in", "Admin")
                    st.success(f"Welcome, Admin {username}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        else:  # Client
            username = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.button("LOGIN AS CLIENT", type="primary"):
                row = c.execute("SELECT client_id, password FROM users WHERE username=?", (username,)).fetchone()
                if row and check_password(pw, row[1]):
                    st.session_state.authenticated = True
                    st.session_state.client_id = row[0]
                    client_data = pd.read_sql(f"SELECT * FROM clients WHERE id = {row[0]}", conn).iloc[0]
                    st.session_state.current_client = client_data.to_dict()
                    add_log("Login", f"Client {client_data['name']} logged in", "Client", row[0])
                    st.success(f"Welcome, {client_data['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    st.stop()

# ------------------------- LOGIN SYSTEM -------------------------
if not st.session_state.get("authenticated", False):
    st.title("KMFX EA Dashboard")
    st.markdown("### Premium Trading Management Portal")

    col1, col2 = st.columns([1, 3])
    with col1:
        if os.path.exists("kmfx_logo.png"):
            st.image("kmfx_logo.png", width=180)
        else:
            st.markdown("<h1 style='font-size:3rem;'>KMFX</h1>", unsafe_allow_html=True)

    with col2:
        login_type = st.radio("Login as", ["Owner", "Admin", "Client"], horizontal=True)

        if login_type == "Owner":
            pw = st.text_input("Owner Master Password", type="password")
            if st.button("LOGIN AS OWNER", type="primary", use_container_width=True):
                if pw == "@@Kingminted@@100590":
                    st.session_state.authenticated = True
                    st.session_state.is_owner = True
                    st.success("Welcome, Owner!")
                    st.rerun()

        # Admin & Client login (same as before - add here)

    st.stop()
    

# ------------------------- MENU ITEMS (PIONEER ONLY FOR MY REFERRALS - FIXED & REALTIME) -------------------------
if st.session_state.get("is_owner"):
    menu_items = [
        "Dashboard Home", "Client Management", "Profit Sharing", "License Generator",
        "File Vault", "Announcements", "Messages", "Notifications", "Withdrawals",
        "EA Versions", "Reports & Export", "Audit Logs", "Admin Management"
    ]
    icons = ["house", "people", "currency-exchange", "key", "folder", "megaphone",
             "chat", "bell", "credit-card", "robot", "graph-up", "journal-text", "shield"]

elif st.session_state.get("is_admin"):
    menu_items = ["Dashboard Home", "Client Management", "Profit Sharing", "Announcements",
                  "Messages", "File Vault", "Withdrawals"]
    icons = ["house", "people", "currency-exchange", "megaphone", "chat", "folder", "credit-card"]

else:  # Client
    menu_items = ["Dashboard Home", "My Profile", "Profit & Earnings", "My Licenses", "My Files",
                  "Announcements", "Notifications", "Messages", "Withdrawals"]
    icons = ["house", "person", "currency-exchange", "key", "folder", "megaphone", "bell", "chat", "credit-card"]

    # === PIONEER ONLY: ADD "My Referrals" TAB (WITH FRESH DATA CHECK) ===
    refresh_current_client()  # Important: Gets the latest client type from DB
    if st.session_state.current_client.get('type') == "Pioneer":
        menu_items.insert(4, "My Referrals")  # Insert after "My Licenses"
        icons.insert(4, "share")

# ------------------------- TOP RESPONSIVE MENU -------------------------
st.markdown("<div class='menu-container'>", unsafe_allow_html=True)
selected = option_menu(
    menu_title=None,
    options=menu_items,
    icons=icons,
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"display": "flex", "flex-wrap": "wrap", "justify-content": "center", "background": "transparent"},
        "nav-link": {"margin": "4px", "border-radius": "12px"},
        "nav-link-selected": {"font-weight": "600"}
    }
)
st.markdown("</div>", unsafe_allow_html=True)
# ------------------------- MOBILE: DROPDOWN MENU -------------------------
st.markdown("<div class='mobile-menu'>", unsafe_allow_html=True)
mobile_selected = st.selectbox(
    "📱 Menu",
    menu_items,
    index=menu_items.index("Dashboard Home") if "Dashboard Home" in menu_items else 0,
    format_func=lambda x: f"{icons[menu_items.index(x)]} {x}" if x in menu_items else x
)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- HEADER -------------------------
col1, col2, col3 = st.columns([5, 3, 2])
with col1:
    role = "Owner 👑" if st.session_state.is_owner else "Admin" if st.session_state.is_admin else st.session_state.current_client['name']
    st.markdown(f"### Welcome back, {role}")

with col2:
    st.markdown(f"**📅** {datetime.date.today().strftime('%B %d, %Y')}")

with col3:
    c1, c2 = st.columns(2)
    with c1:
        theme_label = "☀️ Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"
        if st.button(theme_label, use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
    with c2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

st.divider()

# ------------------------- PAGE CONTENT (CLEAN PLACEHOLDERS) -------------------------
# ------------------------- SUPER ULTIMATE DASHBOARD HOME (LATEST FIXED - REALTIME KPIs) -------------------------
if selected == "Dashboard Home":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.header("📊 KMFX Elite Command Center")

    # === FORCE FRESH DATA - CLEAR CACHES IF NEEDED ===
    # We clear caches only when necessary (e.g., after actions), but for dashboard, we fetch fresh
    df_clients = load_clients()
    
    # Fresh profits & withdrawals (no cache dependency issue here, but ensure fresh)
    df_profits = pd.read_sql("SELECT profit, client_share, your_share, referral_bonus, date, client_id FROM profits", conn)
    
    df_withdrawals = pd.read_sql("""
        SELECT amount, status, date_requested, date_processed 
        FROM withdrawals
    """, conn)

    # KPIs - REALTIME CALCULATION
    total_revenue = (df_profits['your_share'].sum() or 0) + (df_profits['referral_bonus'].sum() or 0)
    
    # CRITICAL FIX: Only count PAID (not Approved)
    total_paid = df_withdrawals[df_withdrawals['status'] == 'Paid']['amount'].sum() or 0
    
    pending_wd = df_withdrawals[df_withdrawals['status'] == 'Pending']['amount'].sum() or 0
    total_clients = len(df_clients)
    
    today = pd.Timestamp.today().normalize()
    expiry_dates = pd.to_datetime(df_clients['expiry'], errors='coerce')
    active_clients = (expiry_dates.isna() | (expiry_dates > today)).sum()
    
    total_licenses = pd.read_sql("SELECT COUNT(*) FROM client_licenses", conn).iloc[0][0]

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("✅ Paid Withdrawals", f"${total_paid:,.2f}")  # Now realtime!
    col3.metric("⏳ Pending Requests", f"${pending_wd:,.2f}")
    col4.metric("👥 Total Clients", total_clients)
    col5.metric("🟢 Active Clients", active_clients)
    col6.metric("🔑 Licenses Issued", total_licenses)

    st.markdown("---")
    # === 2 COLUMN LAYOUT ===
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("📈 Revenue Growth (Your Share + Referral Bonuses)")
        if not df_profits.empty:
            df_profits['date'] = pd.to_datetime(df_profits['date'], errors='coerce')
            monthly = df_profits.groupby(df_profits['date'].dt.strftime('%Y-%m'))[['your_share', 'referral_bonus']].sum().reset_index()
            monthly = monthly.sort_values('date')
            monthly['total'] = monthly['your_share'] + monthly['referral_bonus']
            fig = px.area(monthly, x='date', y='total',
                          color_discrete_sequence=[accent])
            fig.update_layout(
                template="plotly_dark" if st.session_state.theme == "dark" else "plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Month",
                yaxis_title="Revenue ($)",
                showlegend=False,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Revenue will appear here after first profit recorded.")

        st.subheader("🏆 Top 5 Performing Clients")
        if len(df_clients) > 0:
            top = df_clients.nlargest(5, 'current_equity')[['name', 'type', 'current_equity']]
            top['current_equity'] = top['current_equity'].apply(lambda x: f"${x:,.0f}")
            top = top.rename(columns={'name': 'Client', 'type': 'Type', 'current_equity': 'Equity'})
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.info("Clients will appear as they grow their equity.")

    with col_right:
        st.subheader("📊 Profit Sources Breakdown")
        if not df_profits.empty:
            sources = pd.DataFrame({
                'Source': ['Your Share', 'Referral Bonuses'],
                'Amount': [df_profits['your_share'].sum(), df_profits['referral_bonus'].sum()]
            })
            fig_pie = px.pie(sources, values='Amount', names='Source',
                            color_discrete_sequence=[accent, "#f59e0b"],
                            hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                template="plotly_dark" if st.session_state.theme == "dark" else "plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Profit sources will show after recording profits.")

        st.subheader("💳 Recent Withdrawals")
        recent_wd = df_withdrawals.sort_values(by='date_requested', ascending=False).head(8)
        if not recent_wd.empty:
            for _, wd in recent_wd.iterrows():
                status = "✅ Paid" if wd['status'] == 'Paid' else "👍 Approved" if wd['status'] == 'Approved' else "⏳ Pending" if wd['status'] == 'Pending' else "❌ Rejected"
                st.markdown(f"{status} **${wd['amount']:,.2f}** • {wd['date_requested']}")
        else:
            st.info("No withdrawal activity yet.")

    # === CLIENT PERSONAL DASHBOARD ===
    if not (st.session_state.is_owner or st.session_state.is_admin):
        st.markdown("---")
        st.subheader("🌟 Your Personal Dashboard")
        refresh_current_client()
        client = st.session_state.current_client
        client_id = client['id']
        
        client_profits = pd.read_sql(f"SELECT profit, date, client_share, referral_bonus FROM profits WHERE client_id = {client_id}", conn)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Current Equity", f"${client['current_equity']:,.2f}")
        col2.metric("💸 Withdrawable", f"${client['withdrawable_balance']:,.2f}")
        total_earned = (client_profits['client_share'].sum() or 0) + (client_profits['referral_bonus'].sum() or 0)
        col3.metric("🌟 Total Earned", f"${total_earned:,.2f}")
        col4.metric("📊 Profit Records", len(client_profits))

        if not client_profits.empty and 'profit' in client_profits.columns:
            client_profits['date'] = pd.to_datetime(client_profits['date'], errors='coerce')
            client_profits = client_profits.dropna(subset=['date', 'profit'])
            if not client_profits.empty:
                start_balance = client.get('start_balance', 0)
                client_profits['equity'] = start_balance + client_profits['profit'].cumsum()
                fig_client = px.line(client_profits, x='date', y='equity', title="Your Equity Growth Journey", color_discrete_sequence=[accent])
                fig_client.update_layout(
                    template="plotly_dark" if st.session_state.theme == "dark" else "plotly_white",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=450,
                    xaxis_title="Date",
                    yaxis_title="Equity ($)"
                )
                st.plotly_chart(fig_client, use_container_width=True)
            else:
                st.info("Your equity growth chart will appear after profits are recorded.")
        else:
            st.info("Your equity growth chart will appear after your first profit is recorded.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE CLIENT MANAGEMENT (FINAL FIXED - REFERRALS WORK ON CREATE, REALTIME, NO BUGS) -------------------------
elif selected == "Client Management" and (st.session_state.is_owner or st.session_state.is_admin):
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.header("👥 Client Management")
    st.markdown("#### Complete client control center")

    # Safe columns
    add_column_if_not_exists("clients", "address", "TEXT")
    add_column_if_not_exists("clients", "mobile_number", "TEXT")
    add_column_if_not_exists("clients", "referral_code", "TEXT UNIQUE")
    add_column_if_not_exists("clients", "referred_by", "INTEGER")

    df_clients = load_clients()

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 All Clients", "➕ Add Client", "✏️ Edit Client", "🔑 Set Login"])

    with tab1:
        st.subheader("All Clients")
        search = st.text_input("Search by Name, Mobile, Address, or Referral Code", key="cm_search")

        filtered = df_clients
        if search:
            search_lower = search.lower()
            filtered = df_clients[
                df_clients['name'].str.lower().str.contains(search_lower, na=False) |
                df_clients['mobile_number'].astype(str).str.lower().str.contains(search_lower, na=False) |
                df_clients['address'].astype(str).str.lower().str.contains(search_lower, na=False) |
                df_clients['referral_code'].astype(str).str.lower().str.contains(search_lower, na=False)
            ]

        if filtered.empty:
            st.info("No clients found.")
        else:
            display = filtered.copy()
            display['current_equity'] = display['current_equity'].apply(lambda x: f"${x:,.2f}")
            display['withdrawable_balance'] = display['withdrawable_balance'].apply(lambda x: f"${x:,.2f}")
            display['start_balance'] = display['start_balance'].apply(lambda x: f"${x:,.2f}")
            display['add_date'] = pd.to_datetime(display['add_date'], errors='coerce').dt.strftime('%b %d, %Y')
            display['expiry'] = pd.to_datetime(display['expiry'], errors='coerce').dt.strftime('%b %d, %Y')

            cols = ['name', 'type', 'mobile_number', 'address', 'accounts', 'referral_code', 'referred_by',
            'current_equity', 'withdrawable_balance', 'start_balance', 'add_date', 'expiry']
            display = display[[c for c in cols if c in display.columns]]
            display.rename(columns={
            'name': 'Name', 'type': 'Type', 'mobile_number': 'Mobile', 'address': 'Address',
            'accounts': 'Accounts', 'referral_code': 'Referral Code', 'referred_by': 'Referred By (ID)',
            'current_equity': 'Equity', 'withdrawable_balance': 'Withdrawable',
            'start_balance': 'Start Balance', 'add_date': 'Joined', 'expiry': 'Expiry'
            }, inplace=True)

            st.dataframe(display, use_container_width=True, hide_index=True)

            csv = filtered.to_csv(index=False).encode()
            st.download_button("📥 Export CSV", csv, "KMFX_Clients.csv", "text/csv", use_container_width=True)

    with tab2:
        st.subheader("Add New Client")
        with st.form("add_client_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name *")
                mobile = st.text_input("Mobile Number *")
                client_type = st.selectbox("Type *", ["Regular", "Pioneer"])
                accounts = st.text_input("Accounts *")
            with c2:
                address = st.text_area("Address *")
                start_bal = st.number_input("Starting Balance ($)", min_value=0.0, value=10000.0, step=500.0)
                expiry = st.date_input("Expiry Date", value=datetime.date.today() + datetime.timedelta(days=365))

            # === FINAL ROBUST REFERRAL FIX (WORKS ON CREATE) ===
            pioneers_df = pd.read_sql("SELECT id, name FROM clients WHERE type = 'Pioneer' ORDER BY name", conn)
            
            if pioneers_df.empty:
                st.info("No Pioneer clients yet. Add a Pioneer first to enable referrals.")
                referred_by = 0
                ref_display = "No Referral"
            else:
                ref_options = ["None"] + pioneers_df['name'].tolist()
                ref_name = st.selectbox("Referred By (Pioneer)", ref_options, index=0)
                
                if ref_name == "None":
                    referred_by = 0
                    ref_display = "No Referral"
                else:
                    # Safe & exact match
                    matched = pioneers_df[pioneers_df['name'] == ref_name]
                    if not matched.empty:
                        referred_by = int(matched['id'].iloc[0])
                        ref_display = ref_name
                    else:
                        st.error("Selected Pioneer not found. Please try again.")
                        referred_by = 0
                        ref_display = "Error"

            submit = st.form_submit_button("➕ ADD CLIENT", type="primary")

            if submit:
                if not all([name.strip(), mobile.strip(), address.strip(), accounts.strip()]):
                    st.error("All required fields must be filled!")
                else:
                    try:
                        c.execute("""INSERT INTO clients
                                     (name, type, accounts, expiry, start_balance, current_equity,
                                      withdrawable_balance, add_date, referred_by, address, mobile_number)
                                     VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)""",
                                  (name.strip(), client_type, accounts.strip(), expiry.isoformat(),
                                   start_bal, start_bal, datetime.date.today().isoformat(),
                                   referred_by, address.strip(), mobile.strip()))

                        new_id = c.lastrowid
                        ref_code = generate_referral_code(name.strip(), new_id)
                        c.execute("UPDATE clients SET referral_code = ? WHERE id = ?", (ref_code, new_id))

                        conn.commit()
                        clear_all_caches()  # FULL REALTIME

                        add_log("Client Added", f"{name} ({client_type}) | Referred by: {ref_display} (ID: {referred_by})")

                        st.success(f"✅ Client '{name}' added successfully!\n\n"
                                   f"Referral Code: `{ref_code}`\n"
                                   f"Referred by: {ref_display} (DB ID: {referred_by})")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error adding client: {e}")
                        print(f"Add client error: {e}")

    with tab3:
        st.subheader("Edit Client")
        if df_clients.empty:
            st.info("No clients to edit.")
        else:
            client_map = dict(zip(df_clients['name'], df_clients['id']))
            sel_name = st.selectbox("Select Client", options=list(client_map.keys()))
            client_id = client_map[sel_name]
            client = df_clients[df_clients['id'] == client_id].iloc[0].to_dict()

            with st.form("edit_client_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("Name", value=client['name'])
                    new_mobile = st.text_input("Mobile", value=client.get('mobile_number', ''))
                    new_type = st.selectbox("Type", ["Regular", "Pioneer"], index=0 if client['type'] == "Regular" else 1)
                    new_accounts = st.text_input("Accounts", value=client['accounts'] or "")
                with c2:
                    new_address = st.text_area("Address", value=client.get('address', ''))
                    exp_date = pd.to_datetime(client['expiry'], errors='coerce') or datetime.date.today() + datetime.timedelta(days=365)
                    new_expiry = st.date_input("Expiry", value=exp_date)

                # Referral in Edit - SAME ROBUST FIX
                pioneers_df = pd.read_sql("SELECT id, name FROM clients WHERE type = 'Pioneer'", conn)
                current_ref_name = "None"
                if client.get('referred_by') and client['referred_by'] != 0:
                    ref_df = pd.read_sql(f"SELECT name FROM clients WHERE id = {client['referred_by']}", conn)
                    if not ref_df.empty:
                        current_ref_name = ref_df.iloc[0]['name']

                ref_options = ["None"] + pioneers_df['name'].tolist()
                ref_index = ref_options.index(current_ref_name) if current_ref_name in ref_options else 0
                ref_name = st.selectbox("Referred By (Pioneer)", ref_options, index=ref_index)

                referred_by = 0
                if ref_name != "None":
                    matched = pioneers_df[pioneers_df['name'] == ref_name]
                    if not matched.empty:
                        referred_by = int(matched['id'].iloc[0])

                st.info(f"Equity: ${client['current_equity']:,.2f} | Withdrawable: ${client['withdrawable_balance']:,.2f}")

                if st.form_submit_button("💾 Save Changes", type="primary"):
                    try:
                        old_name = client['name']
                        c.execute("""UPDATE clients
                                     SET name=?, type=?, accounts=?, expiry=?, address=?, mobile_number=?, referred_by=?
                                     WHERE id=?""",
                                  (new_name.strip(), new_type, new_accounts.strip(), new_expiry.isoformat(),
                                   new_address.strip(), new_mobile.strip(), referred_by, client_id))

                        if new_name.strip().lower() != old_name.lower():
                            new_ref_code = generate_referral_code(new_name.strip(), client_id)
                            c.execute("UPDATE clients SET referral_code = ? WHERE id = ?", (new_ref_code, client_id))

                        conn.commit()
                        clear_all_caches()

                        add_log("Client Updated", f"ID {client_id} | {new_name} | Referred by: {ref_name}")

                        st.success("Updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab4:
        st.subheader("Set Client Login")
        if df_clients.empty:
            st.info("No clients yet.")
        else:
            client_map = dict(zip(df_clients['name'], df_clients['id']))
            sel_name = st.selectbox("Select Client", options=list(client_map.keys()), key="login_sel")
            client_id = client_map[sel_name]

            with st.form("set_login_form"):
                username = st.text_input("Username *")
                pw1 = st.text_input("Password *", type="password")
                pw2 = st.text_input("Confirm Password *", type="password")

                if st.form_submit_button("🔐 Set Login", type="primary"):
                    if not username or not pw1:
                        st.error("Username and password required!")
                    elif pw1 != pw2:
                        st.error("Passwords do not match!")
                    elif len(pw1) < 8:
                        st.error("Password must be at least 8 characters!")
                    else:
                        try:
                            hashed = hash_password(pw1)
                            c.execute("INSERT OR REPLACE INTO users (client_id, username, password) VALUES (?, ?, ?)",
                                      (client_id, username.strip(), hashed))
                            conn.commit()
                            clear_all_caches()

                            add_log("Client Login Set", f"Client {sel_name} | Username: {username}")
                            st.success("Login credentials set!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE PROFIT SHARING & EARNINGS (FINAL FIXED - REFERRAL BONUS GUARANTEED WORKING) -------------------------
elif selected == "Profit Sharing" or selected == "Profit & Earnings":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
   
    if st.session_state.is_owner or st.session_state.is_admin:
        # ====================== OWNER / ADMIN VIEW ======================
        st.header("💰 Profit Sharing Management")
        df_clients = load_clients()
       
        if df_clients.empty:
            st.info("No clients yet. Add them in Client Management first.")
        else:
            client_options = {row['name']: row['id'] for _, row in df_clients.iterrows()}
            selected_name = st.selectbox(
                "Select Client",
                options=list(client_options.keys()),
                format_func=lambda x: f"{x} ({df_clients[df_clients['name']==x]['type'].iloc[0]})"
            )
            client_id = client_options[selected_name]
           
            # Fresh client data
            client = pd.read_sql(f"SELECT * FROM clients WHERE id = {client_id}", conn).iloc[0].to_dict()
           
            st.success(f"**Selected:** {client['name']} • {client['type']} • "
                       f"Equity: ${client['current_equity']:,.2f} • "
                       f"Withdrawable: ${client['withdrawable_balance']:,.2f}")
           
            # Profit input
            col1, col2 = st.columns([2, 1])
            with col1:
                profit = st.number_input("Profit / Loss Amount ($)", value=0.0, step=100.0, format="%.2f")
            with col2:
                rec_date = st.date_input("Record Date", value=datetime.date.today())
           
            if st.button("📈 RECORD PROFIT / LOSS", type="primary", use_container_width=True):
                if profit == 0:
                    st.warning("Enter a non-zero amount.")
                else:
                    try:
                        # Base share calculation
                        if client['type'].strip() == "Pioneer":
                            client_share = profit * 0.75 if profit > 0 else 0.0
                        else:
                            client_share = profit * 0.65 if profit > 0 else 0.0
                       
                        owner_share = profit - client_share
                        referral_total = 0.0

                        # === FINAL GUARANTEED REFERRAL BONUS LOGIC ===
                        if profit > 0 and client['type'].strip() == "Regular":
                            current_id = client_id
                            level = 1
                            
                            st.info("🔍 Starting referral bonus trace...")
                            
                            while level <= 3:
                                # Get current client's upline info
                                upline_query = pd.read_sql(f"SELECT referred_by FROM clients WHERE id = {current_id}", conn)
                                if upline_query.empty:
                                    st.warning(f"No client found with ID {current_id}")
                                    break
                                
                                upline_referred_by = upline_query.iloc[0]['referred_by']
                                
                                if pd.isna(upline_referred_by) or upline_referred_by in (0, None):
                                    st.info(f"Level {level}: Reached top of chain (no further upline)")
                                    break
                                
                                pioneer_id = int(upline_referred_by)
                                
                                # Verify that the upline is a Pioneer
                                pioneer_row = pd.read_sql(f"SELECT name, type FROM clients WHERE id = {pioneer_id}", conn)
                                if pioneer_row.empty:
                                    st.warning(f"Pioneer ID {pioneer_id} not found!")
                                    break
                                
                                pioneer_name = pioneer_row.iloc[0]['name']
                                pioneer_type = pioneer_row.iloc[0]['type'].strip()
                                
                                if pioneer_type != "Pioneer":
                                    st.info(f"Level {level}: Upline {pioneer_name} is {pioneer_type} → not Pioneer, stopping.")
                                    break
                                
                                # Calculate bonus
                                rate = {1: 0.06, 2: 0.03, 3: 0.01}[level]
                                bonus = profit * rate
                                referral_total += bonus
                                
                                # Insert separate bonus record
                                c.execute("""INSERT INTO profits
                                             (client_id, profit, date, referral_bonus, client_share, your_share)
                                             VALUES (?, ?, ?, ?, ?, ?)""",
                                          (pioneer_id, 0.0, rec_date.isoformat(), bonus, 0.0, 0.0))
                                
                                # Add bonus to Pioneer's withdrawable balance
                                c.execute("""UPDATE clients 
                                             SET withdrawable_balance = withdrawable_balance + ?
                                             WHERE id = ?""",
                                          (bonus, pioneer_id))
                                
                                st.success(f"✅ Level {level} Bonus: +${bonus:.2f} → {pioneer_name} (Pioneer)")
                                
                                # Move to next level
                                current_id = pioneer_id
                                level += 1
                        
                        # Deduct total referral bonuses from owner's share
                        owner_share -= referral_total

                        # Main profit record for the client
                        c.execute("""INSERT INTO profits
                                     (client_id, profit, date, client_share, your_share)
                                     VALUES (?, ?, ?, ?, ?)""",
                                  (client_id, profit, rec_date.isoformat(), client_share, owner_share))
                       
                        # Update client balances
                        c.execute("""UPDATE clients
                                     SET current_equity = current_equity + ?,
                                         withdrawable_balance = withdrawable_balance + ?
                                     WHERE id = ?""",
                                  (profit, client_share, client_id))
                       
                        conn.commit()
                        clear_all_caches()
                       
                        st.success(f"✅ Profit recorded successfully!\n"
                                   f"Client earnings: +${client_share:.2f}\n"
                                   f"Referral bonuses distributed: ${referral_total:.2f}\n"
                                   f"Owner net: +${owner_share:.2f}")
                        st.rerun()
                       
                    except Exception as e:
                        st.error(f"Error recording profit: {e}")
                        print(f"MAIN PROFIT ERROR: {e}")
           
            # === PROFIT HISTORY ===
            st.markdown("---")
            st.subheader(f"Profit History - {client['name']}")
            history = pd.read_sql(f"""
                SELECT date, profit, client_share, your_share, referral_bonus
                FROM profits
                WHERE client_id = {client_id}
                ORDER BY date DESC
            """, conn)
           
            if not history.empty:
                history['date'] = pd.to_datetime(history['date']).dt.strftime('%b %d, %Y')
                history['profit'] = history['profit'].apply(lambda x: f"${x:,.2f}")
                history['client_share'] = history['client_share'].apply(lambda x: f"${x:,.2f}" if x else "-")
                history['your_share'] = history['your_share'].apply(lambda x: f"${x:,.2f}" if x else "-")
                history['referral_bonus'] = history['referral_bonus'].apply(lambda x: f"${x:,.2f}" if x else "-")
                st.dataframe(history, use_container_width=True, hide_index=True)
            else:
                st.info("No profit records yet for this client.")
   
    else:
        # ====================== CLIENT VIEW ======================
        st.header("💰 My Profit & Earnings")
        refresh_current_client()
        client = st.session_state.current_client
        client_id = client['id']
       
        col1, col2 = st.columns(2)
        col1.metric("Current Equity", f"${client['current_equity']:,.2f}")
        col2.metric("Withdrawable Earnings", f"${client['withdrawable_balance']:,.2f}")
       
        history = pd.read_sql(f"""
            SELECT date, profit, client_share, referral_bonus
            FROM profits
            WHERE client_id = {client_id}
            ORDER BY date DESC
        """, conn)
       
        if not history.empty:
            st.subheader("Earnings History")
            history['date'] = pd.to_datetime(history['date']).dt.strftime('%b %d, %Y')
            history['profit'] = history['profit'].apply(lambda x: f"${x:,.2f}")
            history['client_share'] = history['client_share'].apply(lambda x: f"${x:,.2f}" if x else "-")
            history['referral_bonus'] = history['referral_bonus'].apply(lambda x: f"${x:,.2f}" if x else "-")
            history['total_earned'] = pd.to_numeric(history['client_share'].str.replace(r'[$,]', '', regex=True), errors='coerce').fillna(0) + \
                                      pd.to_numeric(history['referral_bonus'].str.replace(r'[$,]', '', regex=True), errors='coerce').fillna(0)
            history['total_earned'] = history['total_earned'].apply(lambda x: f"${x:,.2f}")
           
            display_hist = history[['date', 'profit', 'client_share', 'referral_bonus', 'total_earned']]
            display_hist.rename(columns={
                'date': 'Date',
                'profit': 'Recorded Profit',
                'client_share': 'Your Share',
                'referral_bonus': 'Referral Bonus',
                'total_earned': 'Total Earned'
            }, inplace=True)
            st.dataframe(display_hist, use_container_width=True, hide_index=True)
           
            total_earned = history['total_earned'].str.replace(r'[$,]', '', regex=True).astype(float).sum()
            st.success(f"🌟 Lifetime Earnings: ${total_earned:,.2f}")
        else:
            st.info("No earnings recorded yet. Your journey starts with the first profit!")
   
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE LICENSE GENERATOR (LATEST FIXED - CLEAN, FAST, REALTIME) -------------------------
elif selected == "License Generator":
    if not st.session_state.is_owner:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.error("🚫 Access Denied")
        st.write("License Generator is only available to Owner.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.header("🔑 License Generator")
        st.markdown("#### Generate secure EA licenses instantly")

        # Ensure notifications table has read column
        try:
            c.execute("ALTER TABLE notifications ADD COLUMN read INTEGER DEFAULT 0")
            conn.commit()
        except:
            pass

        df_clients = load_clients()

        if df_clients.empty:
            st.info("No clients available yet. Add them in Client Management first.")
            st.stop()

        # Client selector
        client_options = {row['name']: row['id'] for _, row in df_clients.iterrows()}
        selected_name = st.selectbox(
            "Select Client",
            options=list(client_options.keys()),
            format_func=lambda x: f"{x} ({df_clients[df_clients['name']==x]['type'].iloc[0]})"
        )
        client_id = client_options[selected_name]
        client = df_clients[df_clients['id'] == client_id].iloc[0]

        st.info(f"""
        **Client:** {client['name']} ({client['type']})  
        **Accounts:** {client['accounts'] or 'Not set'}  
        **Current Expiry:** {client.get('expiry', 'None')}
        """)

        # License options
        col1, col2 = st.columns(2)
        with col1:
            new_expiry = st.date_input(
                "New Expiry Date",
                value=datetime.date.today() + datetime.timedelta(days=365),
                min_value=datetime.date.today()
            )
            version = st.text_input("Version Name (optional)", placeholder="e.g. v3.5 Elite Pro")
        with col2:
            allow_live = st.checkbox("Allow Live Trading", value=True)
            live_status = "LIVE" if allow_live else "DEMO ONLY"

        st.markdown("---")

        if st.button("🔐 GENERATE LICENSE", type="primary", use_container_width=True):
            try:
                # Generate unique key
                today_str = datetime.date.today().strftime("%b%d%Y").upper()
                unique_key = f"KMFX_{client['name'].upper().replace(' ', '_')}_{today_str}"

                # Plain data for encryption
                plain_data = f"{client['name']}|{client['accounts'] or ''}|{new_expiry}|{'1' if allow_live else '0'}"
                enc_key = unique_key
                enc_data = ''.join(
                    format(ord(plain_data[i]) ^ ord(enc_key[i % len(enc_key)]), '02X')
                    for i in range(len(plain_data))
                )

                # Save to database
                c.execute("""INSERT INTO client_licenses
                             (client_id, key, enc_data, version, date_generated, expiry, allow_live)
                             VALUES (?, ?, ?, ?, ?, ?, ?)""",
                          (client_id, unique_key, enc_data, version or "Latest",
                           datetime.date.today().isoformat(), new_expiry.isoformat(),
                           1 if allow_live else 0))

                # Update client expiry
                c.execute("UPDATE clients SET expiry = ? WHERE id = ?", (new_expiry.isoformat(), client_id))
                conn.commit()

                # === REALTIME: Clear cache for instant KPI update ===
                load_clients.clear()

                # === SEND NOTIFICATION TO CLIENT ===
                notification_message = f"""
**New EA License Generated!** 🔑

**Client:** {client['name']}  
**Version:** {version or 'Latest'}  
**Expiry:** {new_expiry.strftime('%B %d, %Y')}  
**Trading:** {'🟢 Live Allowed' if allow_live else '🔴 Demo Only'}

You can now view and download your license from **My Licenses** page.

Thank you for being part of KMFX Elite!  
Built by Faith, Shared for Generations.
                """.strip()

                try:
                    c.execute("""INSERT INTO notifications
                                 (client_id, title, message, category, date, read)
                                 VALUES (?, ?, ?, ?, ?, 0)""",
                              (client_id, "🔑 New License Issued!", notification_message, "License", datetime.date.today().isoformat()))
                    conn.commit()
                    noti_success = True
                except Exception as e_notif:
                    noti_success = False
                    print(f"Notification error: {e_notif}")

                # === SUCCESS DISPLAY ===
                st.success(f"✅ License generated successfully for **{client['name']}**!")
                if noti_success:
                    st.info("🔔 Client notified instantly via Notifications!")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.code(f"UNIQUE_KEY = \"{unique_key}\"", language="text")
                with col_b:
                    st.code(f"ENC_DATA = \"{enc_data}\"", language="text")

                # Download file
                license_content = f"""KMFX EA LICENSE
=====================
Client: {client['name']}
Unique Key: {unique_key}
Encrypted Data: {enc_data}
Version: {version or 'Latest'}
Generated: {datetime.date.today().strftime('%B %d, %Y')}
Expiry: {new_expiry.strftime('%B %d, %Y')}
Live Trading: {live_status}
=====================
Thank you for trusting KMFX Elite.
Built by Faith, Shared for Generations.
"""

                st.download_button(
                    label="📥 Download License File",
                    data=license_content,
                    file_name=f"KMFX_License_{client['name'].replace(' ', '_')}_{today_str}_{live_status}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                add_log("License Generated", f"{client['name']} | {version or 'Latest'} | {live_status} | Expiry: {new_expiry}")

            except Exception as e:
                st.error(f"Error generating license: {e}")
                print(f"License gen error: {e}")

        # === RECENT LICENSES FOR THIS CLIENT ===
        st.markdown("---")
        st.subheader("Recent Licenses (This Client)")
        recent = pd.read_sql(f"""
            SELECT date_generated, expiry, allow_live, version
            FROM client_licenses
            WHERE client_id = {client_id}
            ORDER BY date_generated DESC
            LIMIT 7
        """, conn)

        if not recent.empty:
            today = datetime.date.today()
            for _, r in recent.iterrows():
                try:
                    exp_date = pd.to_datetime(r['expiry']).date() if r['expiry'] else None
                    status = "🟢 Active" if (exp_date is None or exp_date >= today) else "🔴 Expired"
                except:
                    status = "⚠️ Invalid"

                live = "Live" if r['allow_live'] else "Demo"
                ver = r['version'] or 'Latest'
                st.markdown(f"• {status} **{r['date_generated']}** → {r['expiry'] or 'No expiry'} | {live} | {ver}")
        else:
            st.info("No previous licenses for this client.")

        st.markdown("</div>", unsafe_allow_html=True)
        
# ------------------------- SUPER ULTIMATE FILE VAULT / MY FILES -------------------------
elif selected == "File Vault" or selected == "My Files":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    if st.session_state.is_owner or st.session_state.is_admin:
        # ====================== OWNER / ADMIN VIEW ======================
        st.header("📁 File Vault")
        st.markdown("#### Securely send files to clients")

        df_clients = load_clients()
        if df_clients.empty:
            st.info("No clients available yet. Add them in Client Management first.")
        else:
            # Client selector
            client_options = {row['name']: row['id'] for _, row in df_clients.iterrows()}
            selected_name = st.selectbox(
                "Select Client to Send Files",
                options=list(client_options.keys())
            )
            client_id = client_options[selected_name]

            # File upload form
            with st.form("send_files_form", clear_on_submit=True):
                notes = st.text_area("Notes (optional)", placeholder="e.g. Latest EA update instructions")
                uploaded_files = st.file_uploader(
                    "Choose files to send",
                    accept_multiple_files=True,
                    key="admin_upload"
                )

                send = st.form_submit_button("📤 SEND FILES TO CLIENT", type="primary", use_container_width=True)

                if send:
                    if not uploaded_files:
                        st.error("Please select at least one file.")
                    else:
                        try:
                            sender = "Owner" if st.session_state.is_owner else "Admin"
                            for file in uploaded_files:
                                safe_filename = f"{client_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"
                                file_path = f"uploaded_files/client_files/{safe_filename}"
                                with open(file_path, "wb") as f:
                                    f.write(file.getbuffer())

                                c.execute("""INSERT INTO client_files 
                                             (client_id, file_name, original_name, upload_date, sent_by, notes)
                                             VALUES (?, ?, ?, ?, ?, ?)""",
                                          (client_id, safe_filename, file.name,
                                           datetime.date.today().isoformat(), sender, notes or ""))

                            conn.commit()
                            add_log("Files Sent", f"{len(uploaded_files)} file(s) to client ID {client_id} ({selected_name})")
                            st.success(f"✅ {len(uploaded_files)} file(s) sent successfully to {selected_name}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error sending files: {e}")

            # Recent sent files to this client
            st.markdown("---")
            st.subheader("Recently Sent to This Client")
            recent_sent = pd.read_sql(f"""
                SELECT original_name, upload_date, sent_by, notes
                FROM client_files
                WHERE client_id = {client_id}
                ORDER BY upload_date DESC
                LIMIT 10
            """, conn)

            if not recent_sent.empty:
                for _, row in recent_sent.iterrows():
                    st.markdown(f"**{row['original_name']}** • Sent on {row['upload_date']} by {row['sent_by']}")
                    if row['notes']:
                        st.caption(f"Notes: {row['notes']}")
            else:
                st.info("No files sent to this client yet.")

    else:
        # ====================== CLIENT VIEW ======================
        st.header("📁 My Files")
        st.markdown("#### Files sent to you by the team")

        client_id = st.session_state.client_id

        files = pd.read_sql(f"""
            SELECT original_name, upload_date, sent_by, notes, file_name
            FROM client_files
            WHERE client_id = {client_id}
            ORDER BY upload_date DESC
        """, conn)

        if files.empty:
            st.info("No files have been sent to you yet.\n\n"
                    "New EA updates, instructions, and resources will appear here.")
        else:
            st.success(f"You have {len(files)} file(s) available")

            for _, row in files.iterrows():
                with st.expander(f"📎 {row['original_name']} • Sent on {row['upload_date']} by {row['sent_by']}"):
                    if row['notes']:
                        st.write(f"**Notes:** {row['notes']}")

                    file_path = f"uploaded_files/client_files/{row['file_name']}"
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="📥 Download File",
                                data=f.read(),
                                file_name=row['original_name'],
                                mime="application/octet-stream",
                                use_container_width=True,
                                key=f"client_dl_{row.name}"
                            )
                    else:
                        st.error("File not found on server. Contact support.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE ANNOUNCEMENTS (WITH PROPER COMMENTS & DELETE) -------------------------
elif selected == "Announcements":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    # === CREATE COMMENTS TABLE IF NOT EXISTS ===
    c.execute('''CREATE TABLE IF NOT EXISTS announcement_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        announcement_id INTEGER,
        commenter_name TEXT,
        comment TEXT,
        timestamp TEXT,
        FOREIGN KEY (announcement_id) REFERENCES announcements (id)
    )''')
    conn.commit()

    if st.session_state.is_owner or st.session_state.is_admin:
        # ====================== POST NEW ANNOUNCEMENT ======================
        st.header("📢 Announcements")
        st.markdown("#### Post updates with images and files")

        with st.form("post_announcement", clear_on_submit=True):
            title = st.text_input("Title *")
            message = st.text_area("Message *", height=200)
            files = st.file_uploader("Attach images or files", accept_multiple_files=True)

            if st.form_submit_button("📢 POST ANNOUNCEMENT", type="primary"):
                if not title.strip() or not message.strip():
                    st.error("Title and message are required!")
                else:
                    try:
                        poster = "Owner" if st.session_state.is_owner else "Admin"
                        c.execute("""INSERT INTO announcements 
                                     (title, message, date, posted_by, likes)
                                     VALUES (?, ?, ?, ?, 0)""",
                                  (title, message, datetime.date.today().isoformat(), poster))
                        ann_id = c.lastrowid

                        if files:
                            for file in files:
                                safe_name = f"{ann_id}_{file.name}"
                                path = f"uploaded_files/announcements/{safe_name}"
                                with open(path, "wb") as f:
                                    f.write(file.getbuffer())
                                c.execute("""INSERT INTO announcement_files 
                                             (announcement_id, file_name, original_name)
                                             VALUES (?, ?, ?)""",
                                          (ann_id, safe_name, file.name))

                        conn.commit()
                        add_log("Announcement Posted", title)
                        st.success("Announcement posted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.markdown("---")

    # ====================== DISPLAY ANNOUNCEMENTS (ALL USERS) ======================
    st.subheader("Latest Announcements")

    # Add likes column if missing
    try:
        c.execute("ALTER TABLE announcements ADD COLUMN likes INTEGER DEFAULT 0")
        conn.commit()
    except:
        pass

    announcements = pd.read_sql("""
        SELECT id, title, message, date, posted_by, likes
        FROM announcements
        ORDER BY date DESC
        LIMIT 20
    """, conn)

    if announcements.empty:
        st.info("No announcements yet. Stay tuned for updates!")
    else:
        for _, ann in announcements.iterrows():
            with st.expander(f"📢 {ann['title']} • {ann['date']} • by {ann['posted_by']} • ❤️ {ann['likes']} likes", expanded=True):
                st.write(ann['message'])

                # === IMAGE PREVIEWS ===
                atts = pd.read_sql(f"SELECT file_name, original_name FROM announcement_files WHERE announcement_id = {ann['id']}", conn)
                images = []
                files = []

                for _, att in atts.iterrows():
                    path = f"uploaded_files/announcements/{att['file_name']}"
                    if os.path.exists(path):
                        if att['original_name'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp')):
                            images.append((path, att['original_name']))
                        else:
                            files.append((path, att['original_name']))

                if images:
                    st.markdown("**Images:**")
                    cols = st.columns(min(3, len(images)))
                    for i, (img_path, name) in enumerate(images):
                        with cols[i % 3]:
                            st.image(img_path, caption=name, use_column_width=True)

                if files:
                    st.markdown("**Files:**")
                    for file_path, name in files:
                        with open(file_path, "rb") as f:
                            st.download_button(f"📎 {name}", f.read(), file_name=name, use_container_width=True)

                # === LIKE BUTTON ===
                if st.button(f"❤️ Like ({ann['likes']})", key=f"like_{ann['id']}"):
                    c.execute("UPDATE announcements SET likes = likes + 1 WHERE id = ?", (ann['id'],))
                    conn.commit()
                    st.rerun()

                # === COMMENTS SECTION ===
                st.markdown("**💬 Comments**")

                # Post new comment
                with st.form(key=f"comment_form_{ann['id']}", clear_on_submit=True):
                    comment_text = st.text_input("Write a comment...", key=f"input_{ann['id']}")
                    col_send, _ = st.columns([1, 4])
                    with col_send:
                        send = st.form_submit_button("Send")

                    if send and comment_text.strip():
                        commenter = (st.session_state.current_client['name'] 
                                     if not (st.session_state.is_owner or st.session_state.is_admin) 
                                     else "Owner/Admin")
                        c.execute("""INSERT INTO announcement_comments 
                                     (announcement_id, commenter_name, comment, timestamp)
                                     VALUES (?, ?, ?, ?)""",
                                  (ann['id'], commenter, comment_text.strip(), datetime.datetime.now().isoformat()))
                        conn.commit()
                        add_log("Comment", f"{commenter} on '{ann['title']}'")
                        st.success("Comment posted!")
                        st.rerun()

                # Display comments
                comments = pd.read_sql(f"""
                    SELECT commenter_name, comment, timestamp, id
                    FROM announcement_comments
                    WHERE announcement_id = {ann['id']}
                    ORDER BY timestamp ASC
                """, conn)

                if not comments.empty:
                    for _, com in comments.iterrows():
                        col_name, col_comment, col_delete = st.columns([2, 6, 1])
                        with col_name:
                            st.caption(f"**{com['commenter_name']}** • {com['timestamp'][:16].replace('T', ' ')}")
                        with col_comment:
                            st.write(com['comment'])
                        with col_delete:
                            if st.session_state.is_owner or st.session_state.is_admin:
                                if st.button("🗑️", key=f"del_com_{com['id']}"):
                                    c.execute("DELETE FROM announcement_comments WHERE id = ?", (com['id'],))
                                    conn.commit()
                                    add_log("Comment Deleted", f"ID {com['id']} on announcement {ann['id']}")
                                    st.rerun()
                else:
                    st.caption("No comments yet. Be the first!")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE MESSAGES SYSTEM (FULLY FIXED) -------------------------
elif selected == "Messages":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    # Define accent color based on current theme (SAFE INSIDE BLOCK)
    if st.session_state.theme == "dark":
        accent_color = "#3b82f6"  # Blue for dark
        bubble_bg_client = "rgba(15, 25, 50, 0.8)"
    else:
        accent_color = "#2563eb"  # Blue for light
        bubble_bg_client = "rgba(255, 255, 255, 0.9)"

    # ====================== OWNER / ADMIN VIEW ======================
    if st.session_state.is_owner or st.session_state.is_admin:
        st.header("💬 Messages Center")
        st.markdown("#### Private support chat with clients")

        conversations = pd.read_sql("""
            SELECT c.id, c.name,
                   COUNT(m.id) as total_msgs,
                   COUNT(CASE WHEN m.read = 0 AND m.from_client_id IS NOT NULL THEN 1 END) as unread
            FROM clients c
            LEFT JOIN messages m ON m.from_client_id = c.id OR m.to_client_id = c.id
            GROUP BY c.id, c.name
            ORDER BY MAX(m.timestamp) DESC, c.name
        """, conn)

        if conversations.empty:
            st.info("No messages yet. Clients will appear here when they send a message.")
        else:
            total_unread = conversations['unread'].sum()
            if total_unread > 0:
                st.success(f"📬 You have {total_unread} unread message(s)")

            client_map = dict(zip(conversations['name'], conversations['id']))
            selected_name = st.selectbox(
                "Select Client Conversation",
                options=list(client_map.keys()),
                format_func=lambda x: f"{x} {'🟢 ' + str(conversations[conversations['name']==x]['unread'].iloc[0]) + ' new' if conversations[conversations['name']==x]['unread'].iloc[0] > 0 else ''}"
            )
            selected_id = client_map[selected_name]

            # Mark as read
            c.execute("UPDATE messages SET read = 1 WHERE from_client_id = ? AND read = 0", (selected_id,))
            conn.commit()

            # Chat thread
            thread = pd.read_sql(f"""
                SELECT from_client_id, from_admin, message, timestamp
                FROM messages
                WHERE from_client_id = {selected_id} OR to_client_id = {selected_id}
                ORDER BY timestamp ASC
            """, conn)

            chat_container = st.container()
            with chat_container:
                for _, msg in thread.iterrows():
                    time_str = pd.to_datetime(msg['timestamp']).strftime('%b %d, %H:%M')
                    if msg['from_client_id']:
                        # Client message
                        st.markdown(f"""
                        <div style="text-align: left; margin: 15px 0;">
                            <div style="display: inline-block; background: {bubble_bg_client}; padding: 12px 18px; border-radius: 18px; max-width: 70%; backdrop-filter: blur(10px);">
                                <p style="margin:0;"><strong>{selected_name}</strong><br>{msg['message']}</p>
                                <small style="opacity: 0.7;">{time_str}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Admin message
                        sender = msg['from_admin'] or "Support"
                        st.markdown(f"""
                        <div style="text-align: right; margin: 15px 0;">
                            <div style="display: inline-block; background: {accent_color}; padding: 12px 18px; border-radius: 18px; max-width: 70%; color: white;">
                                <p style="margin:0;"><strong>You ({sender})</strong><br>{msg['message']}</p>
                                <small style="opacity: 0.8;">{time_str}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # Reply form
            st.markdown("---")
            with st.form("reply_form", clear_on_submit=True):
                reply_text = st.text_area("Type your reply", height=100)
                reply_files = st.file_uploader("Attach files", accept_multiple_files=True, key=f"reply_files_{selected_id}")

                if st.form_submit_button("📤 Send Reply", type="primary", use_container_width=True):
                    if not reply_text and not reply_files:
                        st.error("Write a message or attach a file.")
                    else:
                        try:
                            sender = "Owner" if st.session_state.is_owner else "Admin"
                            c.execute("""INSERT INTO messages 
                                         (from_admin, to_client_id, message, timestamp)
                                         VALUES (?, ?, ?, ?)""",
                                      (sender, selected_id, reply_text or "", datetime.datetime.now().isoformat()))
                            msg_id = c.lastrowid

                            if reply_files:
                                for file in reply_files:
                                    safe_name = f"{msg_id}_{file.name}"
                                    path = f"uploaded_files/messages/{safe_name}"
                                    with open(path, "wb") as f:
                                        f.write(file.getbuffer())
                                    c.execute("""INSERT INTO message_attachments 
                                                 (message_id, file_name, original_name)
                                                 VALUES (?, ?, ?)""",
                                              (msg_id, safe_name, file.name))

                            conn.commit()
                            add_log("Message Sent", f"To client {selected_name}")
                            st.success("Reply sent!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # ====================== CLIENT VIEW ======================
    else:
        st.header("💬 Support Messages")
        st.markdown("#### Chat with the KMFX team")

        client_id = st.session_state.client_id

        thread = pd.read_sql(f"""
            SELECT message, timestamp, from_admin IS NOT NULL as from_admin
            FROM messages
            WHERE from_client_id = {client_id} OR to_client_id = {client_id}
            ORDER BY timestamp ASC
        """, conn)

        chat_container = st.container()
        with chat_container:
            if thread.empty:
                st.info("No messages yet. Start the conversation below!")
            else:
                for _, msg in thread.iterrows():
                    time_str = pd.to_datetime(msg['timestamp']).strftime('%b %d, %H:%M')
                    if msg['from_admin']:
                        # Admin message
                        st.markdown(f"""
                        <div style="text-align: left; margin: 15px 0;">
                            <div style="display: inline-block; background: {accent_color}; padding: 12px 18px; border-radius: 18px; max-width: 70%; color: white;">
                                <strong>Support Team</strong><br>{msg['message']}<br>
                                <small style="opacity: 0.8;">{time_str}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Client message
                        st.markdown(f"""
                        <div style="text-align: right; margin: 15px 0;">
                            <div style="display: inline-block; background: {bubble_bg_client}; padding: 12px 18px; border-radius: 18px; max-width: 70%; backdrop-filter: blur(10px);">
                                <strong>You</strong><br>{msg['message']}<br>
                                <small style="opacity: 0.7;">{time_str}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # Send message form
        st.markdown("---")
        with st.form("client_message_form", clear_on_submit=True):
            client_message = st.text_area("Your message to support", height=100)
            client_files = st.file_uploader("Attach files", accept_multiple_files=True, key="client_upload")

            if st.form_submit_button("📤 Send Message", type="primary", use_container_width=True):
                if not client_message and not client_files:
                    st.error("Write a message or attach a file.")
                else:
                    try:
                        c.execute("""INSERT INTO messages 
                                     (from_client_id, message, timestamp)
                                     VALUES (?, ?, ?)""",
                                  (client_id, client_message or "", datetime.datetime.now().isoformat()))
                        msg_id = c.lastrowid

                        if client_files:
                            for file in client_files:
                                safe_name = f"{msg_id}_{file.name}"
                                path = f"uploaded_files/messages/{safe_name}"
                                with open(path, "wb") as f:
                                    f.write(file.getbuffer())
                                c.execute("""INSERT INTO message_attachments 
                                             (message_id, file_name, original_name)
                                             VALUES (?, ?, ?)""",
                                          (msg_id, safe_name, file.name))

                        conn.commit()
                        add_log("Message Received", f"From client ID {client_id}")
                        st.success("Message sent to support!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE NOTIFICATIONS (FULLY FIXED & RICH) -------------------------
elif selected == "Notifications":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    if st.session_state.is_owner or st.session_state.is_admin:
        st.info("📢 This page is for client personal notifications only.")
        st.write("You send notifications through actions like License Generator, Withdrawals, etc.")
        st.stop()

    st.header("🔔 Notifications")
    st.markdown("#### Important updates and alerts for your account")

    client_id = st.session_state.client_id

    # Ensure table has 'read' column
    try:
        c.execute("ALTER TABLE notifications ADD COLUMN read INTEGER DEFAULT 0")
        conn.commit()
    except:
        pass

    # Fetch notifications
    notifications = pd.read_sql(f"""
        SELECT id, title, message, category, date, read
        FROM notifications
        WHERE client_id = {client_id}
        ORDER BY read ASC, date DESC
    """, conn)

    unread_count = notifications[notifications['read'] == 0].shape[0]

    if unread_count > 0:
        st.success(f"🟢 You have {unread_count} unread notification(s)")

        if st.button("✅ Mark All as Read", type="primary", use_container_width=True):
            try:
                c.execute(f"UPDATE notifications SET read = 1 WHERE client_id = {client_id} AND read = 0")
                conn.commit()
                st.success("All notifications marked as read!")
                st.rerun()
            except Exception as e:
                st.error(f"Error marking all as read: {e}")

    if notifications.empty:
        st.info("No notifications yet.\n\n"
                "You will be notified here for:\n"
                "• New EA licenses\n"
                "• Withdrawal status changes\n"
                "• Important announcements\n"
                "• Messages from support")
    else:
        for _, noti in notifications.iterrows():
            # Category icons
            icon = {
                'License': '🔑',
                'Withdrawal': '💳',
                'General': '📢',
                'Message': '✉️',
                'Profit': '💰',
                'System': '⚙️'
            }.get(noti['category'], '🔔')

            status_badge = "🟢 NEW" if noti['read'] == 0 else "✅ Read"

            with st.expander(f"{status_badge} {icon} {noti['title']} • {noti['date']} • {noti['category']}", expanded=(noti['read'] == 0)):
                st.markdown(noti['message'])

                if noti['read'] == 0:
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("Mark as Read", key=f"read_single_{noti['id']}"):
                            try:
                                c.execute("UPDATE notifications SET read = 1 WHERE id = ?", (noti['id'],))
                                conn.commit()
                                st.success("Marked as read!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

    # Auto-refresh for real-time feel
    if 'notif_timer' not in st.session_state:
        st.session_state.notif_timer = 30

    st.caption(f"🔄 Auto-refresh in {st.session_state.notif_timer} seconds...")
    import time
    time.sleep(1)
    st.session_state.notif_timer -= 1
    if st.session_state.notif_timer <= 0:
        st.session_state.notif_timer = 30
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE WITHDRAWALS MANAGEMENT (WITH CLEAR 1-3 DAYS NOTE) -------------------------
elif selected == "Withdrawals":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    # ====================== ADMIN / OWNER VIEW ======================
    if st.session_state.is_owner or st.session_state.is_admin:
        st.header("💳 Withdrawal Management")
        st.markdown("#### Approve requests and mark as paid when processed")

        pending = pd.read_sql("""
            SELECT w.id, w.amount, w.method, w.details, w.date_requested, w.status,
                   c.name, c.withdrawable_balance, c.mobile_number, c.address
            FROM withdrawals w
            JOIN clients c ON w.client_id = c.id
            WHERE w.status = 'Pending'
            ORDER BY w.date_requested DESC
        """, conn)

        approved_pending_payout = pd.read_sql("""
            SELECT w.id, w.amount, w.method, w.details, w.date_requested, w.date_processed,
                   c.name, c.withdrawable_balance
            FROM withdrawals w
            JOIN clients c ON w.client_id = c.id
            WHERE w.status = 'Approved'
            ORDER BY w.date_processed DESC
        """, conn)

        if pending.empty and approved_pending_payout.empty:
            st.success("✅ No pending withdrawal actions at the moment.")
        else:
            if not pending.empty:
                st.warning(f"⏳ {len(pending)} pending approval request(s)")
                for _, req in pending.iterrows():
                    with st.expander(f"⏳ ${req['amount']:,.2f} • {req['name']} • Requested: {req['date_requested']}", expanded=True):
                        st.write(f"**Client:** {req['name']}")
                        st.write(f"**Mobile:** {req['mobile_number'] or 'Not set'}")
                        st.write(f"**Address:** {req['address'] or 'Not set'}")
                        st.write(f"**Current Withdrawable:** ${req['withdrawable_balance']:,.2f}")
                        st.write(f"**Details:**\n{req['details']}")

                        col_approve, col_reject = st.columns(2)
                        with col_approve:
                            if st.button("✅ APPROVE", key=f"approve_{req['id']}", type="primary"):
                                try:
                                    c.execute("""UPDATE withdrawals
                                                 SET status = 'Approved',
                                                     date_processed = ?,
                                                     processed_by = ?
                                                 WHERE id = ?""",
                                              (datetime.date.today().isoformat(),
                                               "Owner" if st.session_state.is_owner else "Admin",
                                               req['id']))
                                    conn.commit()

                                    # === NOTIFICATION WITH 1-3 DAYS NOTE ===
                                    try:
                                        c.execute("""INSERT INTO notifications
                                                     (client_id, title, message, category, date, read)
                                                     VALUES (
                                                         (SELECT client_id FROM withdrawals WHERE id = ?),
                                                         '💳 Withdrawal Approved!',
                                                         ?,
                                                         'Withdrawal',
                                                         ?,
                                                         0
                                                     )""",
                                                  (req['id'],
                                                   f"Your withdrawal request of ${req['amount']:,.2f} has been **APPROVED**! 🎉\n\n"
                                                   f"**Payment will be sent within 1-3 working days** via {req['method']}.\n\n"
                                                   f"Please check your account after that period.\n\n"
                                                   f"Thank you for trading with KMFX Elite!",
                                                   datetime.date.today().isoformat()))
                                        conn.commit()
                                    except:
                                        pass

                                    add_log("Withdrawal Approved", f"${req['amount']:,.2f} for {req['name']}")
                                    st.success("Approved! Client notified with processing time.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

                        with col_reject:
                            reject_reason = st.text_input("Reason for rejection", key=f"reason_{req['id']}")
                            if st.button("❌ REJECT", key=f"reject_{req['id']}", type="secondary"):
                                if not reject_reason.strip():
                                    st.error("Reason required.")
                                else:
                                    try:
                                        c.execute("""UPDATE withdrawals SET status = 'Rejected', notes = ? WHERE id = ?""",
                                                  (reject_reason, req['id']))
                                        conn.commit()
                                        try:
                                            c.execute("""INSERT INTO notifications
                                                         (client_id, title, message, category, date, read)
                                                         VALUES (
                                                             (SELECT client_id FROM withdrawals WHERE id = ?),
                                                             'Withdrawal Rejected',
                                                             ?,
                                                             'Withdrawal',
                                                             ?,
                                                             0
                                                         )""",
                                                      (req['id'],
                                                       f"Your withdrawal was rejected.\nReason: {reject_reason}",
                                                       datetime.date.today().isoformat()))
                                            conn.commit()
                                        except:
                                            pass
                                        add_log("Withdrawal Rejected", f"${req['amount']:,.2f} | {reject_reason}")
                                        st.error("Rejected.")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {e}")

            if not approved_pending_payout.empty:
                st.markdown("---")
                st.subheader("✅ Approved - Awaiting Payout (1-3 Working Days)")
                for _, req in approved_pending_payout.iterrows():
                    with st.expander(f"👍 ${req['amount']:,.2f} • {req['name']} • Approved: {req['date_processed']}", expanded=False):
                        st.write(f"**Client:** {req['name']}")
                        st.write(f"**Current Withdrawable:** ${req['withdrawable_balance']:,.2f}")
                        st.write(f"**Details:** {req['details']}")
                        st.info("⏳ Client has been informed: Payment within 1-3 working days")
                        if st.button("💰 MARK AS PAID (Deduct Balance)", key=f"paid_{req['id']}", type="secondary", use_container_width=True):
                            try:
                                c.execute("""UPDATE clients
                                             SET withdrawable_balance = withdrawable_balance - ?
                                             WHERE id = (SELECT client_id FROM withdrawals WHERE id = ?)""",
                                          (req['amount'], req['id']))
                                c.execute("UPDATE withdrawals SET status = 'Paid' WHERE id = ?", (req['id'],))
                                conn.commit()

                                # Final paid notification
                                try:
                                    c.execute("""INSERT INTO notifications
                                                 (client_id, title, message, category, date, read)
                                                 VALUES (
                                                     (SELECT client_id FROM withdrawals WHERE id = ?),
                                                     '✅ Withdrawal Paid!',
                                                     ?,
                                                     'Withdrawal',
                                                     ?,
                                                     0
                                                 )""",
                                              (req['id'],
                                               f"Great news! Your withdrawal of ${req['amount']:,.2f} has been **PAID**! 💸\n\n"
                                               f"Check your {req['method']} account now.\n\n"
                                               f"Thank you for being part of KMFX Elite!",
                                               datetime.date.today().isoformat()))
                                    conn.commit()
                                except:
                                    pass

                                add_log("Withdrawal Paid", f"${req['amount']:,.2f} for {req['name']}")
                                st.success("Marked as PAID! Balance deducted.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

    # ====================== CLIENT VIEW ======================
    else:
        st.header("💳 My Withdrawals")
        st.markdown("#### Request payout of your earnings")

        refresh_current_client()
        client = st.session_state.current_client
        withdrawable = client['withdrawable_balance']
        st.metric("Available for Withdrawal", f"${withdrawable:,.2f}")

        if withdrawable < 10:
            st.warning("Minimum withdrawal amount is $10.")
        else:
            with st.form("withdrawal_request"):
                amount = st.number_input("Amount ($)", min_value=10.0, max_value=float(withdrawable), step=10.0)
                method = st.selectbox("Payment Method", ["GCash", "Bank Transfer", "USDT", "PayMaya", "PayPal", "Other"])
                details = st.text_area("Payment Details (e.g. GCash number, Bank account) *")

                if st.form_submit_button("📤 SUBMIT REQUEST", type="primary"):
                    if not details.strip():
                        st.error("Payment details are required!")
                    else:
                        try:
                            c.execute("""INSERT INTO withdrawals
                                         (client_id, amount, method, details, date_requested, status)
                                         VALUES (?, ?, ?, ?, ?, 'Pending')""",
                                      (client['id'], amount, method, details, datetime.date.today().isoformat()))
                            conn.commit()

                            # === CLEAR SUCCESS MESSAGE WITH 1-3 DAYS NOTE ===
                            st.success(f"✅ Withdrawal request for ${amount:,.2f} submitted successfully!\n\n"
                                       f"**Status:** Pending Approval\n"
                                       f"**Processing Time:** Once approved, payment will be sent within **1-3 working days**.\n\n"
                                       f"You will receive a notification for every update.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        # History
        st.markdown("---")
        st.subheader("Withdrawal History")
        history = pd.read_sql(f"SELECT * FROM withdrawals WHERE client_id = {client['id']} ORDER BY date_requested DESC", conn)
        if history.empty:
            st.info("No withdrawal history yet.")
        else:
            for _, row in history.iterrows():
                if row['status'] == 'Paid':
                    icon = "✅"
                    extra = ""
                elif row['status'] == 'Approved':
                    icon = "👍"
                    extra = " (Payment processing: 1-3 working days)"
                elif row['status'] == 'Rejected':
                    icon = "❌"
                    extra = f" - Reason: {row['notes'] or 'Not specified'}"
                else:
                    icon = "⏳"
                    extra = ""

                st.markdown(f"{icon} **${row['amount']:,.2f}** • {row['method']} • {row['date_requested']} • Status: **{row['status']}**{extra}")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE MY REFERRALS (FINAL FIXED - NO NAMEERROR, PERFECT TREE) -------------------------
elif selected == "My Referrals":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    
    if st.session_state.is_owner or st.session_state.is_admin:
        st.info("👑 This page is exclusive for Pioneer members.")
        st.write("Pioneers can view their downline and referral earnings here.")
        st.stop()
    
    refresh_current_client()
    client = st.session_state.current_client
    
    if client['type'] != "Pioneer":
        st.error("🚫 Access Denied")
        st.write("My Referrals is only available to Pioneer members.")
        st.stop()
    
    st.header("🌳 My Referrals")
    st.markdown("#### Your downline network & referral earnings")
    
    client_id = client['id']
    
    # === STATS ===
    ref_bonus_total = pd.read_sql(f"""
        SELECT COALESCE(SUM(referral_bonus), 0) FROM profits WHERE client_id = {client_id}
    """, conn).iloc[0][0]
    
    direct_refs = pd.read_sql(f"SELECT COUNT(*) FROM clients WHERE referred_by = {client_id}", conn).iloc[0][0]
    
    total_downline_df = pd.read_sql(f"""
        WITH RECURSIVE downline(id) AS (
            SELECT id FROM clients WHERE referred_by = {client_id}
            UNION ALL
            SELECT c.id FROM clients c JOIN downline d ON c.referred_by = d.id
        )
        SELECT COUNT(*) FROM downline
    """, conn)
    total_downline = total_downline_df.iloc[0][0] if not total_downline_df.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎁 Total Referral Bonus", f"${ref_bonus_total:,.2f}")
    col2.metric("👥 Direct Referrals", direct_refs)
    col3.metric("🌐 Total Downline", total_downline + direct_refs)
    col4.metric("🔗 Your Referral Code", f"`{client.get('referral_code', 'N/A')}`")
    
    st.code(f"https://yourdomain.com/register?ref={client.get('referral_code', 'yourcode')}", language="text")
    
    st.markdown("---")
    
    # === FIXED REFERRAL TREE (NO NAMEERROR) ===
    st.subheader("🌿 Your Referral Tree")
    st.markdown("#### Visual network of your growing downline")

    def build_tree(cid):
        children_df = pd.read_sql(f"SELECT id, name, type FROM clients WHERE referred_by = {cid}", conn)
        tree = []
        for _, child in children_df.iterrows():
            tree.append({
                "name": child['name'],
                "type": child['type'],
                "children": build_tree(child['id'])
            })
        return tree

    tree_data = build_tree(client_id)

    if not tree_data:
        st.info("🌱 Your downline is growing! Share your referral code to build your powerful network.")
    else:
        def display_tree(nodes, prefix="", is_last=True, depth=0):
            for i, node in enumerate(nodes):
                is_last_node = i == len(nodes) - 1
                branch = "└── " if is_last_node else "├── "
                connector = "    " if is_last_node else "│   "

                badge = "👑 <span style='color:#fbbf24; font-weight:bold;'>Pioneer Leader</span>" if node['type'] == "Pioneer" else "👤 <span style='color:#94a3b8;'>Regular Member</span>"

                glow = "text-shadow: 0 0 10px rgba(59,130,246,0.7);" if depth == 0 else ""
                st.markdown(f"{prefix}{branch} <strong style='font-size:1.1rem; {glow}'>{node['name']}</strong> • {badge}", unsafe_allow_html=True)

                new_prefix = prefix + connector
                if node['children']:
                    display_tree(node['children'], new_prefix, is_last_node, depth + 1)

        # Premium container
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(15, 25, 50, 0.9), rgba(30, 41, 79, 0.8));
            backdrop-filter: blur(16px);
            border-radius: 20px;
            padding: 32px;
            border: 2px solid rgba(59, 130, 246, 0.4);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3), 0 0 20px rgba(59,130,246,0.2);
            font-family: 'Courier New', monospace;
            font-size: 17px;
            line-height: 2.2;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        ">
            <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%); pointer-events: none; animation: pulse 8s infinite;"></div>
            <style>@keyframes pulse {0% {transform: translate(50%,50%) scale(1); opacity: 0.3;} 50% {opacity: 0.5;} 100% {transform: translate(50%,50%) scale(1.2); opacity: 0.2;}}</style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center; margin-bottom:30px;">
            <div style="display:inline-block; padding:15px 40px; background:{accent}; border-radius:50px; color:white; font-size:1.4rem; font-weight:bold; box-shadow:0 0 20px rgba(59,130,246,0.6);">
                🌟 {client['name']} (You) • Pioneer Leader
            </div>
        </div>
        """, unsafe_allow_html=True)

        display_tree(tree_data, depth=0)
        st.markdown("</div>", unsafe_allow_html=True)

        st.caption("👑 Pioneer Leader • 👤 Regular Member • Deeper levels = stronger growth")

    # === BONUS HISTORY (keep the amazing style from before) ===
    st.markdown("---")
    st.subheader("🎁 Referral Bonus History")
    st.markdown("#### Your earnings from downline profits – pure passive income!")

    bonus_history = pd.read_sql(f"""
        SELECT p.date, p.referral_bonus, c.name AS from_client
        FROM profits p
        JOIN clients c ON p.client_id = c.id
        WHERE p.referral_bonus > 0
          AND p.client_id IN (
            WITH RECURSIVE downline(id) AS (
                SELECT id FROM clients WHERE referred_by = {client_id}
                UNION ALL
                SELECT c.id FROM clients c JOIN downline d ON c.referred_by = d.id
            )
            SELECT id FROM downline UNION SELECT {client_id}
        )
        ORDER BY p.date DESC
    """, conn)

    if bonus_history.empty:
        st.info("🌟 Referral bonuses will appear here once your downline starts generating profits.\n\nThe more active your network, the bigger your passive earnings!")
    else:
        total_bonus = bonus_history['referral_bonus'].sum()
        st.markdown(f"""
        <div style="text-align:center; margin:30px 0;">
            <div style="display:inline-block; padding:20px 60px; background:linear-gradient(135deg, #1e3a8a, #3b82f6); border-radius:30px; color:white; font-size:2rem; font-weight:bold; box-shadow:0 0 30px rgba(59,130,246,0.8);">
                Total Referral Earnings: ${total_bonus:,.2f} 💎
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(15, 25, 50, 0.9), rgba(30, 41, 79, 0.8));
            backdrop-filter: blur(16px);
            border-radius: 20px;
            padding: 20px;
            border: 2px solid rgba(251, 191, 36, 0.4);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3), 0 0 25px rgba(251,191,36,0.2);
        ">
        """, unsafe_allow_html=True)

        for _, row in bonus_history.iterrows():
            date_str = pd.to_datetime(row['date']).strftime('%b %d, %Y')
            bonus_str = f"${row['referral_bonus']:,.2f}"
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 18px 24px;
                margin: 12px 0;
                background: rgba(59, 130, 246, 0.15);
                border-radius: 16px;
                border-left: 6px solid #fbbf24;
                box-shadow: 0 4px 15px rgba(251,191,36,0.2);
            ">
                <div style="flex: 1;">
                    <div style="font-size:1.2rem; font-weight:bold; color:#fbbf24;">🏆 Bonus Earned</div>
                    <div style="color:#e2e8f0; margin-top:8px;">From: <strong>{row['from_client']}</strong></div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.8rem; font-weight:bold; color:#fbbf24; text-shadow: 0 0 15px rgba(251,191,36,0.6);">
                        +{bonus_str}
                    </div>
                    <div style="color:#94a3b8; font-size:0.9rem; margin-top:4px;">{date_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.caption("💡 Every profit from your downline = automatic bonus. Build deeper, earn forever!")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE EA VERSIONS MANAGEMENT (OWNER ONLY) -------------------------
elif selected == "EA Versions":
    if not st.session_state.is_owner:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.error("🚫 Access Denied")
        st.write("EA Versions Management is only available to Owner.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.header("🤖 EA Versions Management")
        st.markdown("#### Upload and distribute new EA builds securely")

        # Ensure folder exists
        os.makedirs("uploaded_files", exist_ok=True)

        # Upload form
        with st.form("upload_ea_form", clear_on_submit=True):
            version_name = st.text_input("Version Name *", placeholder="e.g. v3.5 Ultimate Pro")
            release_notes = st.text_area("Release Notes (optional)", placeholder="List new features, fixes, improvements...")
            ea_file = st.file_uploader(
                "Upload EA File (.ex4, .ex5, .mq4, .mq5)",
                type=["ex4", "ex5", "mq4", "mq5"],
                key="ea_upload"
            )

            upload_btn = st.form_submit_button("📤 UPLOAD NEW VERSION", type="primary", use_container_width=True)

            if upload_btn:
                if not version_name.strip():
                    st.error("Version name is required!")
                elif not ea_file:
                    st.error("Please select an EA file to upload!")
                else:
                    try:
                        # Safe filename
                        safe_filename = f"KMFX_EA_{version_name.replace(' ', '_').replace('.', '_')}_{ea_file.name}"
                        file_path = f"uploaded_files/{safe_filename}"

                        # Save file
                        with open(file_path, "wb") as f:
                            f.write(ea_file.getbuffer())

                        # Save to database
                        c.execute("""INSERT INTO ea_versions 
                                     (version, file_name, upload_date, notes)
                                     VALUES (?, ?, ?, ?)""",
                                  (version_name.strip(), safe_filename,
                                   datetime.date.today().isoformat(), release_notes.strip() or "No notes"))
                        conn.commit()

                        add_log("EA Version Uploaded", f"{version_name} - {ea_file.name}")
                        st.success(f"✅ EA Version '{version_name}' uploaded successfully!")

                        # Show immediate preview
                        st.balloons()

                    except Exception as e:
                        st.error(f"Error uploading EA: {e}")

        st.markdown("---")

        # Available versions list
        st.subheader("Available EA Versions")

        versions = pd.read_sql("""
            SELECT version, file_name, upload_date, notes
            FROM ea_versions
            ORDER BY upload_date DESC
        """, conn)

        if versions.empty:
            st.info("No EA versions uploaded yet. Upload the first one above!")
        else:
            for _, v in versions.iterrows():
                with st.expander(f"📦 {v['version']} • Uploaded: {v['upload_date']}", expanded=False):
                    if v['notes']:
                        st.write(f"**Release Notes:**\n{v['notes']}")

                    file_path = f"uploaded_files/{v['file_name']}"
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="📥 Download EA File",
                                data=f.read(),
                                file_name=v['file_name'],
                                mime="application/octet-stream",
                                use_container_width=True,
                                key=f"ea_dl_{v.name}"
                            )
                    else:
                        st.error("File missing on server. Contact developer.")

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE REPORTS & EXPORT (OWNER ONLY) -------------------------
elif selected == "Reports & Export":
    if not st.session_state.is_owner:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.error("🚫 Access Denied")
        st.write("Reports & Export is only available to Owner.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.header("📈 Reports & Export")
        st.markdown("#### Comprehensive data reports and CSV exports")

        # Load all data
        df_clients = load_clients()
        df_profits = load_profits_summary()
        df_withdrawals = pd.read_sql("SELECT * FROM withdrawals", conn)
        df_logs = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", conn)

        tab1, tab2, tab3, tab4 = st.tabs(["💰 Profit Reports", "👥 Client Summary", "💳 Withdrawals Report", "📜 Full Audit Logs"])

        with tab1:
            st.subheader("Profit & Revenue Reports")

            if df_profits.empty:
                st.info("No profit records yet. Reports will populate after recording profits.")
            else:
                # Full profits with client names
                profits_full = pd.read_sql("""
                    SELECT p.*, c.name, c.type
                    FROM profits p
                    JOIN clients c ON p.client_id = c.id
                    ORDER BY p.date DESC
                """, conn)

                profits_full['date'] = pd.to_datetime(profits_full['date']).dt.strftime('%b %d, %Y')

                # Format currency
                for col in ['profit', 'client_share', 'your_share', 'referral_bonus']:
                    profits_full[col] = profits_full[col].apply(lambda x: f"${x:,.2f}" if x else "$0.00")

                st.dataframe(profits_full, use_container_width=True, hide_index=True)

                # Totals
                total_profit = df_profits['profit'].sum()
                total_client_share = df_profits['client_share'].sum()
                total_owner_share = df_profits['your_share'].sum()
                total_referral = df_profits['referral_bonus'].sum()

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Recorded Profit", f"${total_profit:,.2f}")
                col2.metric("Client Shares Paid", f"${total_client_share:,.2f}")
                col3.metric("Your Revenue", f"${total_owner_share:,.2f}")
                col4.metric("Referral Bonuses", f"${total_referral:,.2f}")

                # Export
                csv_profits = profits_full.to_csv(index=False).encode()
                st.download_button(
                    "📥 Export Profit Report CSV",
                    csv_profits,
                    "KMFX_Profit_Report.csv",
                    "text/csv",
                    use_container_width=True
                )

        with tab2:
            st.subheader("Client Summary Report")

            if df_clients.empty:
                st.info("No clients yet.")
            else:
                clients_report = df_clients.copy()
                clients_report['current_equity'] = clients_report['current_equity'].apply(lambda x: f"${x:,.2f}")
                clients_report['withdrawable_balance'] = clients_report['withdrawable_balance'].apply(lambda x: f"${x:,.2f}")
                clients_report['start_balance'] = clients_report['start_balance'].apply(lambda x: f"${x:,.2f}")
                clients_report['add_date'] = pd.to_datetime(clients_report['add_date']).dt.strftime('%b %d, %Y')
                clients_report['expiry'] = pd.to_datetime(clients_report['expiry'], errors='coerce').dt.strftime('%b %d, %Y')

                cols = ['name', 'type', 'mobile_number', 'address', 'accounts', 'referral_code',
                        'current_equity', 'withdrawable_balance', 'start_balance', 'add_date', 'expiry']
                clients_report = clients_report[[c for c in cols if c in clients_report.columns]]
                clients_report.rename(columns={
                    'name': 'Client Name',
                    'type': 'Type',
                    'mobile_number': 'Mobile',
                    'address': 'Address',
                    'accounts': 'Accounts',
                    'referral_code': 'Referral Code',
                    'current_equity': 'Current Equity',
                    'withdrawable_balance': 'Withdrawable',
                    'start_balance': 'Start Balance',
                    'add_date': 'Joined',
                    'expiry': 'Expiry'
                }, inplace=True)

                st.dataframe(clients_report, use_container_width=True, hide_index=True)

                csv_clients = df_clients.to_csv(index=False).encode()
                st.download_button(
                    "📥 Export Client Summary CSV",
                    csv_clients,
                    "KMFX_Client_Summary.csv",
                    "text/csv",
                    use_container_width=True
                )

        with tab3:
            st.subheader("Withdrawals Report")

            if df_withdrawals.empty:
                st.info("No withdrawal records yet.")
            else:
                wd_report = pd.read_sql("""
                    SELECT w.*, c.name, c.type
                    FROM withdrawals w
                    JOIN clients c ON w.client_id = c.id
                    ORDER BY w.date_requested DESC
                """, conn)

                wd_report['date_requested'] = pd.to_datetime(wd_report['date_requested']).dt.strftime('%b %d, %Y')
                if 'date_processed' in wd_report.columns:
                    wd_report['date_processed'] = pd.to_datetime(wd_report['date_processed'], errors='coerce').dt.strftime('%b %d, %Y')

                wd_report['amount'] = wd_report['amount'].apply(lambda x: f"${x:,.2f}")

                st.dataframe(wd_report, use_container_width=True, hide_index=True)

                csv_wd = wd_report.to_csv(index=False).encode()
                st.download_button(
                    "📥 Export Withdrawals Report CSV",
                    csv_wd,
                    "KMFX_Withdrawals_Report.csv",
                    "text/csv",
                    use_container_width=True
                )

        with tab4:
            st.subheader("Full Audit Logs Export")

            if df_logs.empty:
                st.info("No logs yet.")
            else:
                logs_display = df_logs.copy()
                logs_display['timestamp'] = pd.to_datetime(logs_display['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

                st.dataframe(logs_display, use_container_width=True, hide_index=True)

                csv_logs = df_logs.to_csv(index=False).encode()
                st.download_button(
                    "📥 Export Full Audit Logs CSV",
                    csv_logs,
                    f"KMFX_Audit_Logs_{datetime.date.today().isoformat()}.csv",
                    "text/csv",
                    use_container_width=True
                )

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE AUDIT LOGS (FULLY FIXED - NO ERRORS) -------------------------
elif selected == "Audit Logs":
    if not st.session_state.is_owner:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.error("🚫 Access Denied")
        st.write("Audit Logs are only available to Owner.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.header("📜 Audit Logs")
        st.markdown("#### Complete system activity history with advanced filtering")

        # Load all logs safely
        all_logs = pd.read_sql("""
            SELECT timestamp, action, details, user_type, user_id
            FROM logs
            ORDER BY timestamp DESC
        """, conn)

        if all_logs.empty:
            st.info("No activity logged yet. All actions will appear here in real-time.")
        else:
            # Filters
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                action_filter = st.multiselect(
                    "Filter by Action",
                    options=sorted(all_logs['action'].unique()),
                    default=[]
                )
            with col2:
                type_filter = st.multiselect(
                    "Filter by User Type",
                    options=sorted(all_logs['user_type'].dropna().unique()),
                    default=[]
                )
            with col3:
                search_text = st.text_input("Search in Details")
            with col4:
                if 'timestamp' in all_logs.columns and not all_logs.empty:
                    min_date = pd.to_datetime(all_logs['timestamp']).min().date()
                    max_date = pd.to_datetime(all_logs['timestamp']).max().date()
                    date_range = st.date_input(
                        "Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                else:
                    date_range = None

            # Apply filters
            filtered = all_logs.copy()
            if 'timestamp' in filtered.columns:
                filtered['date'] = pd.to_datetime(filtered['timestamp'], errors='coerce').dt.date

            if action_filter:
                filtered = filtered[filtered['action'].isin(action_filter)]
            if type_filter:
                filtered = filtered[filtered['user_type'].isin(type_filter)]
            if search_text:
                filtered = filtered[filtered['details'].str.contains(search_text, case=False, na=False)]
            if date_range and len(date_range) == 2:
                filtered = filtered[
                    (filtered['date'] >= date_range[0]) &
                    (filtered['date'] <= date_range[1])
                ]

            # Display count
            st.success(f"📊 Showing {len(filtered)} log entries (out of {len(all_logs)} total)")

            # Formatted display
            display_logs = filtered.copy()
            display_logs['timestamp'] = pd.to_datetime(display_logs['timestamp'], errors='coerce').dt.strftime('%b %d, %Y • %H:%M:%S')

            # === SAFE CLIENT NAME ENRICHMENT (NO KEYERROR) ===
            display_logs['client'] = ""
            if 'user_id' in filtered.columns:
                user_ids = filtered['user_id'].dropna().unique()
                if len(user_ids) > 0:
                    client_names = {}
                    for uid in user_ids:
                        try:
                            name_df = pd.read_sql(f"SELECT name FROM clients WHERE id = {int(uid)}", conn)
                            if not name_df.empty:
                                client_names[int(uid)] = name_df.iloc[0]['name']
                        except:
                            pass
                    display_logs['client'] = display_logs['user_id'].map(client_names).fillna("")

            # Final columns
            display_cols = ['timestamp', 'action', 'details', 'user_type', 'client']
            display_logs = display_logs[[col for col in display_cols if col in display_logs.columns]]

            st.dataframe(display_logs, use_container_width=True, hide_index=True)

            # Export buttons
            csv_filtered = filtered.to_csv(index=False).encode()
            st.download_button(
                "📥 Export Filtered Logs CSV",
                csv_filtered,
                f"KMFX_Audit_Logs_Filtered_{datetime.date.today().isoformat()}.csv",
                "text/csv",
                use_container_width=True
            )

            csv_all = all_logs.to_csv(index=False).encode()
            st.download_button(
                "📥 Export ALL Logs CSV",
                csv_all,
                f"KMFX_Full_Audit_Logs_{datetime.date.today().isoformat()}.csv",
                "text/csv",
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE ADMIN MANAGEMENT (FULLY FIXED - DELETE WORKS 100%) -------------------------
elif selected == "Admin Management":
    if not st.session_state.is_owner:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.error("🚫 Access Denied")
        st.write("Admin Management is only available to Owner.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.header("👤 Admin Management")
        st.markdown("#### Create and manage admin accounts with full control")

        # Ensure name column exists
        try:
            c.execute("ALTER TABLE admins ADD COLUMN name TEXT")
            conn.commit()
        except:
            pass

        # Always fresh admins list
        admins = pd.read_sql("SELECT id, username, name FROM admins ORDER BY username", conn)

        col1, col2 = st.columns([1, 1])

        # === CREATE NEW ADMIN ===
        with col1:
            st.subheader("➕ Create New Admin")
            with st.form("create_admin_form", clear_on_submit=True):
                admin_name = st.text_input("Full Name *")
                admin_username = st.text_input("Username *", placeholder="e.g. admin_john")
                admin_password = st.text_input("Password *", type="password")
                confirm_password = st.text_input("Confirm Password *", type="password")

                if st.form_submit_button("✅ CREATE ADMIN", type="primary", use_container_width=True):
                    if not all([admin_name.strip(), admin_username.strip(), admin_password, confirm_password]):
                        st.error("All fields are required!")
                    elif admin_password != confirm_password:
                        st.error("Passwords do not match!")
                    elif len(admin_password) < 8:
                        st.error("Password must be at least 8 characters!")
                    else:
                        try:
                            hashed_pw = hash_password(admin_password)
                            c.execute("""INSERT INTO admins (username, password, name)
                                         VALUES (?, ?, ?)""",
                                      (admin_username.strip(), hashed_pw, admin_name.strip()))
                            conn.commit()
                            add_log("Admin Created", f"Username: {admin_username} | Name: {admin_name}")
                            st.success(f"✅ Admin '{admin_username}' created successfully!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Username already exists!")
                        except Exception as e:
                            st.error(f"Error: {e}")

        # === CURRENT ADMINS LIST ===
        with col2:
            st.subheader("👥 Current Admins")
            if admins.empty:
                st.info("No admin accounts yet. Create one on the left.")
            else:
                # Session state to track admin selected for deletion
                if 'admin_to_delete' not in st.session_state:
                    st.session_state.admin_to_delete = None

                for _, admin in admins.iterrows():
                    with st.expander(f"👤 {admin['name'] or 'No name set'} • @{admin['username']}"):
                        st.write(f"**ID:** {admin['id']}")
                        st.write(f"**Username:** {admin['username']}")
                        st.write(f"**Name:** {admin['name'] or 'Not set'}")

                        if st.button("🗑️ Delete Admin", key=f"del_btn_{admin['id']}", type="secondary"):
                            st.session_state.admin_to_delete = {
                                'id': admin['id'],
                                'username': admin['username'],
                                'name': admin['name'] or 'No name'
                            }
                            st.rerun()

                # === CONFIRMATION SECTION (OUTSIDE LOOP - NO KEY CONFLICT) ===
                if st.session_state.admin_to_delete:
                    del_info = st.session_state.admin_to_delete
                    st.markdown("---")
                    st.error(f"⚠️ You are about to **permanently delete** the following admin:")
                    st.write(f"**Name:** {del_info['name']}")
                    st.write(f"**Username:** @{del_info['username']}")
                    st.write(f"**ID:** {del_info['id']}")
                    st.warning("This action cannot be undone!")

                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("🔥 YES, DELETE PERMANENTLY", type="primary", use_container_width=True):
                            try:
                                c.execute("DELETE FROM admins WHERE id = ?", (del_info['id'],))
                                conn.commit()
                                add_log("Admin Deleted", f"Username: {del_info['username']}")
                                st.success(f"✅ Admin '@{del_info['username']}' deleted permanently.")
                                st.session_state.admin_to_delete = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting admin: {e}")

                    with col_cancel:
                        if st.button("❌ Cancel", type="secondary", use_container_width=True):
                            st.session_state.admin_to_delete = None
                            st.rerun()

        # === OWNER INFO ===
        st.markdown("---")
        st.subheader("👑 Owner Account (Master)")
        st.info("""
        **Owner privileges cannot be modified or deleted here.**
       
        • Full system access
        • Can create/delete admins
        • Login via Owner Master Password only
       
        Change password directly in code for security.
        """)

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- SUPER ULTIMATE MY PROFILE (REAL-TIME BALANCE FIX) -------------------------
elif selected == "My Profile":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    if st.session_state.is_owner or st.session_state.is_admin:
        st.info("👑 This page is for client personal profile only.")
        st.write("Owner/Admin accounts are managed separately.")
    else:
        st.header("👤 My Profile")
        st.markdown("#### Personal information and account settings")

        # === CRITICAL FIX: FORCE REFRESH CLIENT DATA FROM DATABASE EVERY TIME ===
        refresh_current_client()  # This line is the key!
        client = st.session_state.current_client
        client_id = client['id']

        # Profile Avatar & Basic Info
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"""
                <div style="
                    text-align: center;
                    padding: 20px;
                    background: {surface_color};
                    border-radius: 16px;
                    backdrop-filter: blur(10px);
                    border: 1px solid {border_color};
                ">
                    <div style="
                        width: 120px;
                        height: 120px;
                        background: {accent};
                        color: white;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 3rem;
                        font-weight: bold;
                        margin: 0 auto 16px;
                    ">
                        {client['name'][0].upper()}
                    </div>
                    <h3>{client['name']}</h3>
                    <p style="margin: 4px 0; color: #94a3b8;">{client['type']} Member</p>
                    <p style="margin: 4px 0;">ID: {client_id}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="
                    background: {surface_color};
                    backdrop-filter: blur(10px);
                    border-radius: 16px;
                    padding: 24px;
                    height: 100%;
                    border: 1px solid {border_color};
                ">
                    <h4>📋 Account Details</h4>
                    <table style="width: 100%; font-size: 1.1rem;">
                        <tr><td><strong>Referral Code</strong></td><td><code>{client.get('referral_code', 'N/A')}</code></td></tr>
                        <tr><td><strong>Mobile Number</strong></td><td>{client.get('mobile_number', 'Not set')}</td></tr>
                        <tr><td><strong>Address</strong></td><td>{client.get('address', 'Not set')}</td></tr>
                        <tr><td><strong>Accounts</strong></td><td>{client.get('accounts', 'Not set')}</td></tr>
                        <tr><td><strong>Join Date</strong></td><td>{pd.to_datetime(client.get('add_date')).strftime('%b %d, %Y') if client.get('add_date') else 'N/A'}</td></tr>
                        <tr><td><strong>Expiry Date</strong></td><td>{pd.to_datetime(client.get('expiry')).strftime('%b %d, %Y') if client.get('expiry') else 'No expiry'}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # === EARNINGS SUMMARY (REAL-TIME) ===
        st.subheader("💰 Earnings Summary")
        profits = pd.read_sql(f"SELECT client_share, referral_bonus FROM profits WHERE client_id = {client_id}", conn)
        total_client_share = profits['client_share'].sum() if not profits.empty else 0
        total_referral = profits['referral_bonus'].sum() if not profits.empty else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Your Share from Profits", f"${total_client_share:,.2f}")
        col2.metric("Referral Bonuses", f"${total_referral:,.2f}")
        col3.metric("Total Earnings", f"${total_client_share + total_referral:,.2f}")

        # === CURRENT BALANCES (REAL-TIME FROM REFRESH) ===
        st.markdown("---")
        st.subheader("💳 Current Balances")
        col1, col2 = st.columns(2)
        col1.metric("Current Equity", f"${client['current_equity']:,.2f}")
        col2.metric("Withdrawable Balance", f"${client['withdrawable_balance']:,.2f}")

        # === CHANGE PASSWORD ===
        st.markdown("---")
        st.subheader("🔐 Change Password")
        with st.form("change_password_form"):
            current_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")

            if st.form_submit_button("💾 UPDATE PASSWORD", type="primary", use_container_width=True):
                if not all([current_pw, new_pw, confirm_pw]):
                    st.error("All fields are required!")
                elif new_pw != confirm_pw:
                    st.error("Passwords do not match!")
                elif len(new_pw) < 8:
                    st.error("Password must be at least 8 characters!")
                else:
                    try:
                        row = c.execute("SELECT password FROM users WHERE client_id = ?", (client_id,)).fetchone()
                        if row and check_password(current_pw, row[0]):
                            hashed = hash_password(new_pw)
                            c.execute("UPDATE users SET password = ? WHERE client_id = ?", (hashed, client_id))
                            conn.commit()
                            add_log("Password Changed", f"Client ID {client_id}")
                            st.success("✅ Password updated successfully!")
                            st.balloons()
                        else:
                            st.error("Current password incorrect!")
                    except Exception as e:
                        st.error(f"Error: {e}")

        # === LOGOUT ===
        st.markdown("---")
        if st.button("🚪 Logout from this device", type="secondary", use_container_width=True):
            add_log("Logout", f"Client {client['name']} logged out")
            st.session_state.clear()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("KMFX EA • Built by Faith ,Shared for Generation • Make him Proud")