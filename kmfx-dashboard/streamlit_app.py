import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import sqlite3
import datetime
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from cryptography.fernet import Fernet
import io

# === PAGE CONFIG ===
st.set_page_config(
    page_title="KMFX EA Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CUSTOM CSS ===
st.markdown("""
<style>
    .main {background-color: #0f172a; color: #e2e8f0;}
    .stApp > header {background-color: transparent;}
    [data-testid="stSidebar"] {background-color: #1e293b;}
    .css-1d391kg {padding-top: 1rem;}
    h1, h2, h3 {color: #ffd700; font-weight: bold;}
    .stButton>button {background-color: #ff6d00; color: white; border-radius: 50px;}
    .stButton>button:hover {background-color: #e65b00;}
    .card {background-color: #1e293b; padding: 20px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); margin: 10px 0;}
    .metric-card {background-color: #262730; padding: 20px; border-radius: 15px; text-align: center;}
    .gold-text {color: #ffd700;}
    .orange-text {color: #ff6d00;}
</style>
""", unsafe_allow_html=True)

# === ENCRYPTION KEY ===
ENCRYPT_KEY = b'vLE2n-EXEB9BsPIVJgLwV0i_l89PxWhDgvdKs1DiqR8='  # CHANGE THIS IN PRODUCTION!
cipher = Fernet(ENCRYPT_KEY)

# === DATABASE ===
conn = sqlite3.connect('kmfx_ultimate.db', check_same_thread=False)
c = conn.cursor()

# Tables (no changes)
c.execute('''CREATE TABLE IF NOT EXISTS clients
             (id INTEGER PRIMARY KEY, name TEXT, type TEXT, accounts TEXT, expiry TEXT,
              start_balance REAL, current_balance REAL, contact_no TEXT, email TEXT, address TEXT,
              add_date TEXT, referred_by INTEGER, referral_code TEXT UNIQUE, notes TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS profits
             (id INTEGER PRIMARY KEY, client_id INTEGER, profit REAL, date TEXT,
              client_share REAL, your_share REAL, referral_bonus REAL DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS users
             (client_id INTEGER UNIQUE, username TEXT UNIQUE, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS admins
             (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, name TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY, from_client_id INTEGER, to_owner INTEGER, message TEXT, timestamp TEXT, read INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS announcements
             (id INTEGER PRIMARY KEY, title TEXT, message TEXT, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS ea_versions
             (id INTEGER PRIMARY KEY, version TEXT, file_name TEXT, upload_date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS feedback
             (id INTEGER PRIMARY KEY, client_id INTEGER, rating INTEGER, comment TEXT, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS notifications
             (id INTEGER PRIMARY KEY, client_id INTEGER, title TEXT, message TEXT, date TEXT, read INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS logs
             (id INTEGER PRIMARY KEY, timestamp TEXT, action TEXT, details TEXT)''')
conn.commit()

# === HELPERS (added try-except for SQL errors) ===
def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode() if data else ""

def decrypt_data(enc_data):
    return cipher.decrypt(enc_data.encode()).decode() if enc_data else ""

def add_log(action, details=""):
    try:
        c.execute("INSERT INTO logs (timestamp, action, details) VALUES (?, ?, ?)",
                  (datetime.datetime.now().isoformat(), action, details))
        conn.commit()
    except Exception as e:
        st.error(f"Log error: {e}")

def send_email(to_email, subject, body, attachment=None, attachment_name=None):
    if not to_email:
        return False
    
    FROM_EMAIL = "kmfxea@gmail.com"      # ⚠️ CHANGE
    FROM_PASS = "your_app_password"         # ⚠️ CHANGE
    
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    if attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.getvalue())
        encoders.encode_base64(part)
        filename = attachment_name or f"KMFX_Statement_{datetime.date.today().strftime('%B_%Y')}.pdf"
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(part)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(FROM_EMAIL, FROM_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

def calculate_shares(profit, client_type):
    if client_type == "Pioneer":
        return profit * 0.75, profit * 0.25
    return profit * 0.65, profit * 0.35

def add_notification(client_id, title, message):
    try:
        c.execute("INSERT INTO notifications (client_id, title, message, date) VALUES (?, ?, ?, ?)",
                  (client_id, title, message, datetime.date.today().isoformat()))
        conn.commit()
    except Exception as e:
        st.error(f"Notification error: {e}")

def generate_monthly_pdf(client, history, ref_bonus_this_month):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFillColor(colors.HexColor("#ffd700"))
    p.setFont("Helvetica-Bold", 24)
    p.drawString(1*inch, height - 1*inch, "KMFX Monthly Statement")
    
    p.setFillColor(colors.HexColor("#ff6d00"))
    p.setFont("Helvetica", 14)
    p.drawString(1*inch, height - 1.5*inch, f"Client: {client['name']} ({client['type']})")
    p.drawString(1*inch, height - 1.8*inch, f"Period: {datetime.date.today().strftime('%B %Y')}")
    p.drawString(1*inch, height - 2.1*inch, f"Ending Balance: ${client['current_balance']:,.2f}")
    
    y = height - 3*inch
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, y, "Date")
    p.drawString(2.5*inch, y, "Profit")
    p.drawString(4*inch, y, "Your Share")
    p.drawString(5.5*inch, y, "Ref. Bonus")
    
    y -= 30
    total_profit = 0
    total_share = 0
    if not history.empty:
        for _, row in history.iterrows():
            p.setFont("Helvetica", 11)
            p.drawString(1*inch, y, str(row['date']))
            p.drawString(2.5*inch, y, f"${row['profit']:,.2f}")
            p.drawString(4*inch, y, f"${row['client_share']:,.2f}")
            p.drawString(5.5*inch, y, f"${row['referral_bonus']:,.2f}")
            total_profit += row['profit'] or 0
            total_share += row['client_share'] or 0
            y -= 20
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*inch, y - 20, f"Total Profit: ${total_profit:,.2f}")
    p.drawString(1*inch, y - 50, f"Your Total Earnings: ${total_share + ref_bonus_this_month:,.2f}")
    
    p.save()
    buffer.seek(0)
    return buffer

def license_encrypt(plain, key):
    result = ""
    for i in range(len(plain)):
        c = ord(plain[i])
        k = ord(key[i % len(key)])
        result += f"{c ^ k:02X}"
    return result

def license_decrypt(enc, key):
    result = ""
    for i in range(0, len(enc), 2):
        c = int(enc[i:i+2], 16)
        k = ord(key[(i//2) % len(key)])
        result += chr(c ^ k)
    return result

# Session State
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.is_owner = False
    st.session_state.is_admin = False
    st.session_state.client_id = None
    st.session_state.current_client = None

# Login Page
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #ffd700;'>🔐 KMFX Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        login_type = st.radio("Login as", ["Owner", "Admin", "Client"], horizontal=True)
        
        if login_type == "Owner":
            pw = st.text_input("Owner Password", type="password")
            if st.button("LOGIN AS OWNER", type="primary", use_container_width=True):
                if pw == "@@Kingminted@@100590":  # ⚠️ CHANGE THIS!
                    st.session_state.authenticated = True
                    st.session_state.is_owner = True
                    add_log("Login", "Owner")
                    st.rerun()
                else:
                    st.error("Wrong password")
        
        elif login_type == "Admin":
            username = st.text_input("Admin Username")
            pw = st.text_input("Password", type="password")
            if st.button("LOGIN AS ADMIN", type="primary", use_container_width=True):
                admin = c.execute("SELECT id FROM admins WHERE username=? AND password=?", (username, pw)).fetchone()
                if admin:
                    st.session_state.authenticated = True
                    st.session_state.is_admin = True
                    add_log("Login", f"Admin {username}")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        else:
            username = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.button("LOGIN AS CLIENT", type="primary", use_container_width=True):
                user = c.execute("SELECT client_id FROM users WHERE username=? AND password=?", (username, pw)).fetchone()
                if user:
                    st.session_state.authenticated = True
                    st.session_state.client_id = user[0]
                    client_data = pd.read_sql(f"SELECT * FROM clients WHERE id={user[0]}", conn).iloc[0]
                    st.session_state.current_client = client_data
                    add_log("Login", f"Client {user[0]} - {client_data['name']}")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    st.stop()

# Main Header
st.markdown(f"""
<div style="text-align: center; padding: 20px; background-color: #1e293b; border-radius: 15px; margin-bottom: 30px;">
    <h1 style="color: #ffd700; font-size: 3.5rem;">🧑‍💼 KMFX Dashboard</h1>
    <p style="color: #ff6d00; font-size: 1.5rem;">
        {'Owner Mode - Full Control' if st.session_state.is_owner else
         'Admin Mode' if st.session_state.is_admin else
         f"Welcome {st.session_state.current_client['name']} ({st.session_state.current_client['type']})"}
    </p>
</div>
""", unsafe_allow_html=True)

# Logout
col1, _, col3 = st.columns([3,1,1])
with col3:
    if st.button("🚪 LOGOUT", type="secondary"):
        st.session_state.authenticated = False
        st.session_state.is_owner = False
        st.session_state.is_admin = False
        st.session_state.client_id = None
        st.session_state.current_client = None
        add_log("Logout", "User logged out")
        st.rerun()

# Sidebar Menu (Fixed: Added Announcements to Owner menu too)
with st.sidebar:
    st.image("kmfx-dashboard/kmfx_logo.png", width=200)
    st.markdown("<h2 style='color: #ffd700; text-align: center;'>Menu</h2>", unsafe_allow_html=True)
    
    if st.session_state.is_owner:
        menu_items = ["Dashboard Home", "Client Management", "License Generator", "Profit Sharing & Statements",
                      "Automations & Reports", "Admin Management", "Post Announcement", "Client Messages", "Audit Logs"]
        icons = ["house", "people", "key", "currency-exchange", "robot", "person-gear", "megaphone", "chat", "journal-text"]
    elif st.session_state.is_admin:
        menu_items = ["Dashboard Home", "Client Management", "Profit Sharing & Statements",
                      "Client Messages", "Post Announcement"]
        icons = ["house", "people", "currency-exchange", "chat", "megaphone"]
    else:
        menu_items = ["Dashboard Home", "Profit Sharing & Statements"]
        if st.session_state.current_client['type'] == "Pioneer":
            menu_items.append("My Referral Link")
        icons = ["house", "currency-exchange"] + (["share"] if st.session_state.current_client['type'] == "Pioneer" else [])

    page = option_menu("Navigation", menu_items, icons=icons, menu_icon="list", default_index=0,
                       styles={"container": {"padding": "0!important", "background-color": "#1e293b"},
                               "icon": {"color": "#ff6d00", "font-size": "20px"},
                               "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#262730"},
                               "nav-link-selected": {"background-color": "#ff6d00", "color": "white"}})

# Dashboard Home (no changes, but added check for empty DF)
if page == "Dashboard Home":
    st.header("Dashboard Overview")
    
    if st.session_state.is_owner or st.session_state.is_admin:
        try:
            df_clients = pd.read_sql("SELECT * FROM clients", conn)
            df_profits = pd.read_sql("SELECT your_share, referral_bonus FROM profits", conn)
        except Exception as e:
            st.error(f"DB error: {e}")
            st.stop()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Clients", len(df_clients))
        col2.metric("Pioneer Clients", len(df_clients[df_clients['type'] == "Pioneer"]) if not df_clients.empty else 0)
        
        total_revenue = (df_profits['your_share'].sum() or 0) + (df_profits['referral_bonus'].sum() or 0)
        col3.metric("Total Revenue", f"${total_revenue:,.2f}")
        
        active_clients = len(df_clients)
        if not df_clients.empty and 'expiry' in df_clients.columns:
            expiry_dates = pd.to_datetime(df_clients['expiry'], errors='coerce')
            today = pd.Timestamp.today().normalize()
            active_mask = expiry_dates.isna() | (expiry_dates > today)
            active_clients = len(df_clients[active_mask])
        col4.metric("Active Clients", active_clients)
        
        if not df_profits.empty:
            monthly = df_profits.copy()
            dates = pd.read_sql("SELECT date FROM profits", conn)['date']
            monthly['month'] = pd.to_datetime(dates).dt.to_period('M').astype(str)
            monthly_rev = monthly.groupby('month')[['your_share', 'referral_bonus']].sum()
            monthly_rev['total'] = monthly_rev.sum(axis=1)
            fig = px.line(monthly_rev.reset_index(), x='month', y='total', title="Monthly Revenue")
            fig.update_traces(line_color="#ff6d00")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No profits yet.")
    
    else:  # Client view
        client = st.session_state.current_client
        st.markdown(f"<h2 style='color: #ffd700;'>Welcome back, {client['name']} ({client['type']}) 👋</h2>", unsafe_allow_html=True)
        
        profits_summary = pd.read_sql(f"""
            SELECT SUM(profit) as total_profit, 
                   SUM(client_share) as client_total,
                   SUM(referral_bonus) as ref_total 
            FROM profits WHERE client_id={client['id']}
        """, conn)
        your_share = (profits_summary['client_total'].iloc[0] or 0) + (profits_summary['ref_total'].iloc[0] or 0)
        
        col1, col2 = st.columns(2)
        col1.metric("Current Balance", f"${client['current_balance']:,.2f}")
        col2.metric("Your Total Earnings", f"${your_share:,.2f}")
        
        # Fixed Equity Curve
        equity_df = pd.read_sql(f"""
            SELECT date, 
                   {client['start_balance'] or 0} + SUM(profit) OVER (ORDER BY date) AS equity
            FROM profits 
            WHERE client_id = {client['id']}
            ORDER BY date
        """, conn)
        
        if not equity_df.empty:
            fig = px.line(equity_df, x='date', y='equity', title="Your Equity Growth")
            fig.update_traces(line_color="#ff6d00")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No profit history yet.")
        
        if client['type'] == "Pioneer":
            referred = pd.read_sql(f"SELECT COUNT(*) FROM clients WHERE referred_by={client['id']}", conn).iloc[0][0]
            ref_earn = pd.read_sql(f"SELECT SUM(referral_bonus) FROM profits WHERE client_id={client['id']}", conn).iloc[0][0] or 0
            colr1, colr2 = st.columns(2)
            colr1.metric("Referred Clients", referred)
            colr2.metric("Referral Bonus Earned", f"${ref_earn:,.2f}")

# Profit Sharing & Statements (fixed referral bonus logic)
if page == "Profit Sharing & Statements":
    st.header("Profit Sharing & Statements")
    
    if st.session_state.is_owner or st.session_state.is_admin:
        df = pd.read_sql("SELECT id, name, type, current_balance, email FROM clients", conn)
    else:
        df = pd.DataFrame([st.session_state.current_client.to_dict()])
    
    client_id = st.selectbox("Select Client", df['id'], format_func=lambda x: df[df['id']==x]['name'].iloc[0])
    client = df[df['id']==client_id].iloc[0]
    
    st.markdown(f"**{client['name']}** ({client['type']}) | Balance: ${client['current_balance']:,.2f}")
    
    if st.session_state.is_owner or st.session_state.is_admin:
        profit = st.number_input("Enter Profit/Loss", value=0.0, step=100.0)
        if st.button("RECORD PROFIT"):
            if profit == 0:
                st.warning("Enter non-zero amount")
            else:
                new_balance = client['current_balance'] + profit
                client_share, your_share = calculate_shares(abs(profit), client['type']) if profit > 0 else (0, 0)
                
                # Insert main profit (referral_bonus=0 for main)
                c.execute("""INSERT INTO profits 
                             (client_id, profit, date, client_share, your_share, referral_bonus) 
                             VALUES (?, ?, ?, ?, ?, 0)""",
                          (client_id, profit, datetime.date.today().isoformat(), client_share, your_share))
                
                # Referral bonuses (only if profit > 0, set as client_share for referrer)
                if profit > 0:
                    referrer_row = pd.read_sql(f"SELECT referred_by FROM clients WHERE id={client_id}", conn)
                    if not referrer_row.empty and referrer_row.iloc[0][0]:
                        direct = referrer_row.iloc[0][0]
                        direct_bonus = profit * 0.10
                        c.execute("""INSERT INTO profits 
                                     (client_id, profit, date, client_share, your_share, referral_bonus) 
                                     VALUES (?, ?, ?, ?, 0, ?)""",
                                  (direct, 0, datetime.date.today().isoformat(), direct_bonus, direct_bonus))
                        
                        # 2nd level
                        second = pd.read_sql(f"SELECT id FROM clients WHERE referred_by={direct}", conn)
                        for sid in second['id']:
                            if sid != client_id:
                                second_bonus = profit * 0.05
                                c.execute("""INSERT INTO profits 
                                             (client_id, profit, date, client_share, your_share, referral_bonus) 
                                             VALUES (?, ?, ?, ?, 0, ?)""",
                                          (sid, 0, datetime.date.today().isoformat(), second_bonus, second_bonus))
                
                c.execute("UPDATE clients SET current_balance=? WHERE id=?", (new_balance, client_id))
                conn.commit()
                add_log("Profit Recorded", f"${profit} for {client_id}")
                st.success(f"Recorded! New balance: ${new_balance:,.2f}")
                
                # Email & Notification
                client_email = decrypt_data(client['email'])
                body = f"New profit: \( {profit:,.2f}\nYour share updated.\nNew balance: \){new_balance:,.2f}"
                send_email(client_email, "KMFX Profit Update", body)
                add_notification(client_id, "Profit Update", f"+${profit:,.2f}")
    
    # Monthly PDF (fixed ref_bonus)
    st.markdown("### Monthly Statement")
    if st.button("Generate Monthly PDF"):
        history = pd.read_sql(f"""
            SELECT profit, client_share, referral_bonus, date
            FROM profits
            WHERE client_id={client_id}
            AND strftime('%Y-%m', date) = '{datetime.date.today().strftime('%Y-%m')}'
        """, conn)
        ref_this_month = history['referral_bonus'].sum() if not history.empty else 0
        pdf_buffer = generate_monthly_pdf(client, history, ref_this_month)
        
        st.download_button("Download PDF", pdf_buffer,
                           f"KMFX_Statement_{client['name'].replace(' ', '_')}_{datetime.date.today().strftime('%B_%Y')}.pdf",
                           "application/pdf")
        
        client_email = decrypt_data(client['email'])
        if client_email:
            pdf_buffer.seek(0)
            send_email(client_email, "Monthly KMFX Statement", "Attached is your statement.", pdf_buffer)

# My Referral Link (no changes)
if page == "My Referral Link" and not st.session_state.is_owner and not st.session_state.is_admin:
    st.header("🔗 My Referral Program")
    client = st.session_state.current_client
    
    ref_link = f"https://your-kmfx-dashboard.streamlit.app/?ref={client['referral_code']}"
    st.code(ref_link, language=None)
    st.info("Share to earn 10% direct + 5% 2nd level bonuses!")
    
    direct_refs = pd.read_sql(f"SELECT name, add_date FROM clients WHERE referred_by={client['id']}", conn)
    st.subheader(f"Direct Referrals ({len(direct_refs)})")
    if not direct_refs.empty:
        direct_refs['add_date'] = pd.to_datetime(direct_refs['add_date']).dt.strftime('%b %d, %Y')
        st.dataframe(direct_refs, use_container_width=True)
    else:
        st.info("No referrals yet.")
    
    total_ref_bonus = pd.read_sql(f"SELECT SUM(referral_bonus) FROM profits WHERE client_id={client['id']}", conn).iloc[0][0] or 0
    st.metric("Total Referral Bonus", f"${total_ref_bonus:,.2f}")
    
    st.subheader("🏆 Referral Leaderboard (Top 10)")
    leaderboard = pd.read_sql("""
        SELECT c.name, SUM(p.referral_bonus) as bonus
        FROM profits p
        JOIN clients c ON p.client_id = c.id
        WHERE p.referral_bonus > 0
        GROUP BY c.id
        ORDER BY bonus DESC
        LIMIT 10
    """, conn)
    if not leaderboard.empty:
        leaderboard['Rank'] = range(1, len(leaderboard) + 1)
        leaderboard['bonus'] = leaderboard['bonus'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(leaderboard[['Rank', 'name', 'bonus']], use_container_width=True)
    else:
        st.info("No bonuses yet.")

# Client Management (fixed ref_code gen with lastrowid)
if page == "Client Management" and (st.session_state.is_owner or st.session_state.is_admin):
    st.header("👥 Client Management")
    
    tab1, tab2, tab3 = st.tabs(["Add New Client", "Set Client Login", "All Clients"])
    
    with tab1:
        st.subheader("Add New Client")
        with st.form("add_client"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name *")
                client_type = st.selectbox("Type *", ["Regular", "Pioneer"])
                accounts = st.text_input("Accounts (comma-separated) *")
                start_balance = st.number_input("Starting Balance *", min_value=0.0, value=10000.0)
            with col2:
                email = st.text_input("Email")
                contact_no = st.text_input("Contact Number")
                address = st.text_area("Address")
                expiry = st.date_input("Expiry", value=datetime.date.today() + datetime.timedelta(days=365))
                pioneers = pd.read_sql("SELECT id, name FROM clients WHERE type='Pioneer'", conn)
                referred_by = st.selectbox("Referred By", options=[None] + list(pioneers['id']), format_func=lambda x: pioneers[pioneers['id']==x]['name'].iloc[0] if x else "None")
            
            submitted = st.form_submit_button("ADD CLIENT")
            if submitted:
                if not name or not accounts:
                    st.error("Required fields missing!")
                else:
                    enc_email = encrypt_data(email)
                    enc_contact = encrypt_data(contact_no)
                    enc_address = encrypt_data(address)
                    
                    c.execute("""INSERT INTO clients 
                                 (name, type, accounts, expiry, start_balance, current_balance, contact_no, email, address, add_date, referred_by)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (name, client_type, accounts, expiry.strftime("%Y-%m-%d"), start_balance, start_balance,
                               enc_contact, enc_email, enc_address, datetime.date.today().isoformat(), referred_by))
                    conn.commit()
                    new_id = c.lastrowid
                    ref_code = ''.join(filter(str.isalnum, name.lower())) + str(new_id)
                    c.execute("UPDATE clients SET referral_code=? WHERE id=?", (ref_code, new_id))
                    conn.commit()
                    st.success(f"Added {name}! Code: {ref_code}")
                    add_log("Client Added", name)
                    st.rerun()
    
    with tab2:
        st.subheader("Set Client Login")
        clients_df = pd.read_sql("SELECT id, name FROM clients", conn)
        if not clients_df.empty:
            sel_client = st.selectbox("Select Client", clients_df['id'], format_func=lambda x: clients_df[clients_df['id']==x]['name'].iloc[0])
            with st.form("set_login"):
                username = st.text_input("Username *")
                password = st.text_input("Password *", type="password")
                set_login = st.form_submit_button("SET LOGIN")
                if set_login:
                    if username and password:
                        c.execute("INSERT OR REPLACE INTO users (client_id, username, password) VALUES (?, ?, ?)",
                                  (sel_client, username, password))
                        conn.commit()
                        st.success("Login set!")
                        add_log("Login Set", f"ID {sel_client}")
                    else:
                        st.error("Fields required")
    
    with tab3:
        st.subheader("All Clients")
        all_clients = pd.read_sql("SELECT id, name, type, accounts, current_balance, expiry, add_date, referral_code FROM clients", conn)
        if not all_clients.empty:
            all_clients['current_balance'] = all_clients['current_balance'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(all_clients, use_container_width=True)
        else:
            st.info("No clients.")

# License Generator (no changes)
if page == "License Generator" and st.session_state.is_owner:
    st.header("🔑 License Generator")
    clients_df = pd.read_sql("SELECT id, name, type, expiry, accounts FROM clients", conn)
    if clients_df.empty:
        st.info("No clients.")
    else:
        client_id = st.selectbox("Select Client", clients_df['id'], format_func=lambda x: clients_df[clients_df['id']==x]['name'].iloc[0])
        client = clients_df[clients_df['id']==client_id].iloc[0]
        
        st.write(f"**{client['name']}** ({client['type']}) Expires: {client['expiry']}")
        allow_live = st.checkbox("Allow Live Trading", value=True)
        
        if st.button("GENERATE LICENSE"):
            today_str = datetime.date.today().strftime("%b%d%Y").upper()
            key = f"KMFX_{client['name'].upper().replace(' ', '_')}_{today_str}"
            plain = f"{client['name']}|{client['accounts']}|{client['expiry']}|{'1' if allow_live else '0'}"
            enc_data = license_encrypt(plain, key)
            
            st.code(f"UNIQUE_KEY = \"{key}\"")
            st.code(f"ENC_DATA = \"{enc_data}\"")
            
            add_log("License Generated", f"Client {client['name']}")
            add_notification(client_id, "New License", "Updated license available.")
            st.success("Generated!")

# Automations & Reports (no changes)
if page == "Automations & Reports" and st.session_state.is_owner:
    st.header("🤖 Automations & Reports")
    
    st.subheader("Upload EA Version")
    uploaded = st.file_uploader("Choose .ex5/.mq5", type=["ex5", "mq5"])
    version = st.text_input("Version (e.g., v3.1)")
    
    if st.button("UPLOAD & NOTIFY") and uploaded and version:
        safe_name = f"KMFX_EA_{version}_{uploaded.name}"
        with open(safe_name, "wb") as f:
            f.write(uploaded.getbuffer())
        
        c.execute("INSERT INTO ea_versions (version, file_name, upload_date) VALUES (?, ?, ?)",
                  (version, uploaded.name, datetime.date.today().isoformat()))
        conn.commit()
        
        all_clients = pd.read_sql("SELECT id FROM clients", conn)
        for cid in all_clients['id']:
            add_notification(cid, "New EA Version", f"Version {version} available.")
        
        st.success("Uploaded!")
    
    st.subheader("Version History")
    versions = pd.read_sql("SELECT version, file_name, upload_date FROM ea_versions ORDER BY upload_date DESC", conn)
    if not versions.empty:
        st.dataframe(versions)
    else:
        st.info("No versions.")

# Admin Management (no changes)
if page == "Admin Management" and st.session_state.is_owner:
    st.header("👤 Admin Management")
    with st.form("add_admin"):
        admin_name = st.text_input("Name")
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
        add = st.form_submit_button("ADD ADMIN")
        if add:
            if admin_user and admin_pass:
                c.execute("INSERT INTO admins (name, username, password) VALUES (?, ?, ?)",
                          (admin_name, admin_user, admin_pass))
                conn.commit()
                st.success(f"Added {admin_name}!")
                add_log("Admin Added", admin_user)
            else:
                st.error("Required fields")
    
    admins = pd.read_sql("SELECT name, username FROM admins", conn)
    if not admins.empty:
        st.dataframe(admins)
    else:
        st.info("No admins.")

# Post Announcement (Fixed: Now for both Owner and Admin)
if page == "Post Announcement" and (st.session_state.is_owner or st.session_state.is_admin):
    st.header("📢 Post Announcement")
    with st.form("announcement_form"):
        title = st.text_input("Title *")
        message = st.text_area("Message *", height=200)
        posted = st.form_submit_button("POST TO ALL")
        if posted:
            if not title or not message:
                st.error("Fill required fields.")
            else:
                c.execute("INSERT INTO announcements (title, message, date) VALUES (?, ?, ?)",
                          (title, message, datetime.date.today().isoformat()))
                conn.commit()
                
                all_clients = pd.read_sql("SELECT id FROM clients", conn)
                for cid in all_clients['id']:
                    add_notification(cid, title, message)
                
                st.success("Posted!")
                add_log("Announcement", title)

# Client Messages Page - FINAL FIXED VERSION
if page == "Client Messages" and (st.session_state.is_owner or st.session_state.is_admin):
    st.header("💬 Client Messages Inbox")
    
    # Refresh button
    if st.button("🔄 Refresh Messages", type="primary"):
        st.rerun()
    
    st.markdown("---")
    
    # FIXED QUERY - More robust join and error handling
    try:
        messages = pd.read_sql("""
            SELECT 
                m.id,
                m.from_client_id,
                COALESCE(c.name, 'Unknown Client (ID: ' || m.from_client_id || ')') as name,
                m.message,
                m.timestamp,
                m.read
            FROM messages m
            LEFT JOIN clients c ON m.from_client_id = c.id
            ORDER BY m.timestamp DESC
        """, conn)
        
        if messages.empty:
            st.info("📭 No messages from clients yet. You're all caught up!")
            st.caption("Tip: Click 🔄 Refresh after a client sends a message.")
        else:
            unread = messages[messages['read'] == 0]
            if len(unread) > 0:
                st.success(f"🟥 You have {len(unread)} unread message(s)!")
            
            for _, msg in messages.iterrows():
                status = "🟥 UNREAD" if msg['read'] == 0 else "✅ Read"
                time_clean = msg['timestamp'].split('.')[0].replace('T', ' ')
                
                with st.expander(f"From: {msg['name']} • {time_clean} • {status}", expanded=(msg['read'] == 0)):
                    st.write(msg['message'])
                    
                    if msg['read'] == 0:
                        if st.button("Mark as Read", key=f"read_{msg['id']}"):
                            c.execute("UPDATE messages SET read=1 WHERE id=?", (msg['id'],))
                            conn.commit()
                            st.success("Marked as read!")
                            st.rerun()
                            
    except Exception as e:
        st.error("Error loading messages. Check database.")
        st.code(str(e))

# Audit Logs (NEW: Added the missing page)
if page == "Audit Logs" and st.session_state.is_owner:
    st.header("📜 Audit Logs")
    logs = pd.read_sql("SELECT timestamp, action, details FROM logs ORDER BY timestamp DESC LIMIT 500", conn)
    if not logs.empty:
        logs['timestamp'] = pd.to_datetime(logs['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(logs, use_container_width=True)
    else:
        st.info("No audit logs yet.")

# Client View Extras (no changes)
if not st.session_state.is_owner and not st.session_state.is_admin:
    client = st.session_state.current_client
    client_id = client['id']
    
    st.markdown("---")
    
    # Latest Announcements
    st.subheader("📢 Updates")
    announces = pd.read_sql("SELECT title, message, date FROM announcements ORDER BY date DESC LIMIT 5", conn)
    if not announces.empty:
        for _, a in announces.iterrows():
            with st.expander(f"{a['title']} - {a['date']}"):
                st.write(a['message'])
    else:
        st.info("No updates.")
    
    # My License
    st.subheader("🔑 My License")
    st.code("Contact owner for key.", language=None)
    st.info("License tied to your accounts.")
    
    # Notifications
    st.subheader("🔔 Notifications")
    notifs = pd.read_sql(f"SELECT title, message, date FROM notifications WHERE client_id={client_id} ORDER BY date DESC LIMIT 10", conn)
    if not notifs.empty:
        for _, n in notifs.iterrows():
            st.info(f"**{n['title']}** • {n['date']}\n{n['message']}")
    else:
        st.success("No new notifications.")
    
    # Message Owner
    st.subheader("✉️ Message Owner")
    with st.form("msg_owner"):
        msg_text = st.text_area("Message")
        send = st.form_submit_button("SEND")
        if send:
            if msg_text.strip():
                c.execute("INSERT INTO messages (from_client_id, message, timestamp) VALUES (?, ?, ?)",
                          (client_id, msg_text, datetime.datetime.now().isoformat()))
                conn.commit()
                st.success("Sent!")
                add_notification(0, "New Message", f"From {client['name']}")
            else:
                st.error("Empty message")

# PWA Support
st.markdown("""
<link rel="manifest" href="data:application/manifest+json,{
  "name": "KMFX EA Dashboard",
  "short_name": "KMFX",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#ff6d00",
  "icons": [
    {"src": "https://via.placeholder.com/192x192/ff6d00/000000?text=KMFX", "sizes": "192x192", "type": "image/png"},
    {"src": "https://via.placeholder.com/512x512/ff6d00/000000?text=KMFX", "sizes": "512x512", "type": "image/png"}
  ]
}">
""", unsafe_allow_html=True)

st.caption("© 2025 KMFX EA Dashboard • Fixed & Functional 🚀")

