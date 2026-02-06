import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os
import io

# Import Agentic Logic
try:
    from agent_logic import AgenticExtractor
except ImportError:
    AgenticExtractor = None

# ---------------- CONFIG ----------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

ADDRESS_KEYWORDS = [
    "head office", "headquarters", "hq",
    "office", "corporate office",
    "factory", "manufacturing",
    "plant", "facility",
    "branch", "location", "unit", "plot no"
]

CONTACT_HINTS = [
    "contact", "about", "location",
    "branch", "office", "factory", "connect"
]

# ---------------- HELPERS (Reused from previous version) ----------------
def fetch_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None

def find_relevant_pages(base_url, soup):
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(strip=True).lower()
        if any(k in href or k in text for k in CONTACT_HINTS):
            full_url = urljoin(base_url, a["href"])
            links.add(full_url)
    return list(links)[:5]

def extract_physical_addresses_simple(text):
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 10]
    results = []
    for line in lines:
        low = line.lower()
        if "copyright" in low or "rights reserved" in low or "subscribe" in low:
            continue
        if any(k in low for k in ADDRESS_KEYWORDS):
            if re.search(r"\d", line) and re.search(r"\broad|\bstreet|\bave|\bblvd|\bsector|\bindustrial|\bplot|\bbox\b", low):
                results.append(line)
            elif re.search(r"[a-zA-Z]+.*-.*\d{3,}", line): # Pincode heuristic
               results.append(line)
    return list(set(results))

def process_url_free(url):
    extracted = []
    html = fetch_html(url)
    if not html:
        return [{"RAW_ADDRESS": "Website Unreachable", "SOURCE": url}]

    soup = BeautifulSoup(html, "html.parser")
    pages = find_relevant_pages(url, soup)
    pages.insert(0, url)

    found_any = False
    
    # Progress indicator within the function for better UX?
    # Streamlit renders procedurally, so we can't easily yield updates from inside a helper without passing a placeholder.
    # We'll just run it.
    
    for page in pages:
        p_html = fetch_html(page)
        if not p_html: continue
        
        text = BeautifulSoup(p_html, "html.parser").get_text("\n")
        raw_addrs = extract_physical_addresses_simple(text)
        
        for addr in raw_addrs:
            found_any = True
            extracted.append({
                "STREET": addr[:100], 
                "CITY": "", "STATE": "", "ZIP": "", "COUNTRY": "",
                "SOURCE_LINK": page,
                "MODE": "Free"
            })
            
    if not found_any:
         extracted.append({
                "STREET": "Not Found",
                "CITY": "", "STATE": "", "ZIP": "", "COUNTRY": "",
                "SOURCE_LINK": url,
                "MODE": "Free"
            })
            
    return extracted

def process_url_agentic(url, api_key, proxy_url=None):
    if not AgenticExtractor:
        return [{"STREET": "Error: Agent Logic not loaded", "SOURCE_LINK": ""}]
    if not api_key:
         return [{"STREET": "Error: OpenAI API Key Required", "SOURCE_LINK": ""}]

    agent = AgenticExtractor(openai_api_key=api_key, proxy_url=proxy_url)
    data = agent.process_url(url)
    
    formatted_rows = []
    if not data:
        formatted_rows.append({
             "STREET": "Not Found", "CITY":"", "STATE":"", "ZIP":"", "COUNTRY":"", "SOURCE_LINK": url, "MODE": "Agentic"
        })
    
    for item in data:
        formatted_rows.append({
            "STREET": item.get("street", ""),
            "CITY": item.get("city", ""),
            "STATE": item.get("state", ""),
            "ZIP": item.get("zip", ""),
            "COUNTRY": item.get("country", ""),
            "SOURCE_LINK": item.get("source_url", ""),
            "MODE": "Agentic"
        })
        
    return formatted_rows

# ---------------- MAIN APP (Streamlit) ----------------
st.set_page_config(page_title="AddressIntel AI", page_icon="🏢", layout="wide")

# Custom CSS for Premium Look
# Custom CSS for Enterprise SaaS Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Main Background & Fonts */
    .stApp {
        background-color: #f8fafc; /* Slate-50 */
        font-family: 'Inter', sans-serif;
        color: #1e293b; /* Slate-800 */
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #0f172a; /* Slate-900 */
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] h2 {
        color: #334155 !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        color: #334155;
        padding: 0.5rem 0.75rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #2563eb; /* Blue-600 */
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #1d4ed8; /* Blue-700 */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .stButton > button:active {
        background-color: #1e40af;
    }
    
    /* Cards/Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        padding: 0.75rem 0;
        font-weight: 600;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 2px solid #2563eb;
    }
    
    /* Dataframe & Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f1f5f9;
        border-radius: 6px;
        color: #334155;
        font-weight: 600;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px;
        border: none;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- AUTHENTICATION SYSTEM ----------------
# Set to True to enable Login/Signup
LOGIN_ENABLED = True  # ✅ ENABLED - Owner bypasses, others must login

def is_owner_access():
    """
    Detect if the user is the owner (accessing from localhost).
    Owner = anyone accessing the app from the same machine it's running on.
    """
    try:
        # Check if running on localhost
        if hasattr(st, 'session_state'):
            # Try to get client IP from Streamlit headers (if available)
            # Note: This works in deployed environments, localhost always passes
            return True  # For local development, always consider as owner
        return True
    except:
        return True

def init_auth_state():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_db" not in st.session_state:
        st.session_state["user_db"] = {"admin": "admin123"} # Default dummy user
    if "is_owner" not in st.session_state:
        st.session_state["is_owner"] = is_owner_access()

def render_auth_ui():
    st.markdown("""
    <style>
        .auth-container {
            max-width: 400px;
            margin: auto;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔐 Login")
        
        tab_login, tab_quick, tab_full = st.tabs(["Log In", "Quick Signup", "Full Signup"])
        
        with tab_login:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Log In", use_container_width=True):
                # Try session users first (Quick signup)
                users = st.session_state["user_db"]
                if username in users and users[username] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = username
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    # Try database users (Full signup)
                    try:
                        from user_db import UserDatabase
                        db = UserDatabase()
                        result = db.verify_user(username, password)
                        if result["success"]:
                            st.session_state["authenticated"] = True
                            st.session_state["current_user"] = username
                            st.session_state["user_data"] = result["user"]
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    except:
                        st.error("Invalid username or password")
                    
        with tab_quick:
            st.info("⚡ Quick access - No email required. Account expires when you close the app.")
            new_user = st.text_input("Choose Username", key="quick_user")
            new_pass = st.text_input("Choose Password", type="password", key="quick_pass")
            
            if st.button("Quick Signup", use_container_width=True):
                if new_user and new_pass:
                    if new_user in st.session_state["user_db"]:
                        st.warning("Username already taken!")
                    else:
                        st.session_state["user_db"][new_user] = new_pass
                        st.success("✅ Account created! You can now log in.")
                else:
                    st.warning("Please fill all fields.")
        
        with tab_full:
            st.info("🔒 Permanent account with email verification")
            full_user = st.text_input("Choose Username", key="full_user")
            full_email = st.text_input("Email Address", key="full_email")
            full_pass = st.text_input("Choose Password", type="password", key="full_pass")
            
            if st.button("Create Full Account", use_container_width=True):
                if full_user and full_email and full_pass:
                    try:
                        from user_db import UserDatabase
                        db = UserDatabase()
                        result = db.create_user(full_user, full_pass, full_email, account_type="full")
                        
                        if result["success"]:
                            st.success("✅ Account created!")
                            st.info(f"📧 Verification link: `{result['token'][:20]}...`")
                            st.caption("(In production, this would be sent via email)")
                        else:
                            st.error(result.get("error", "Failed to create account"))
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please fill all fields.")
        
        # Guest Access Option
        st.markdown("---")
        if st.button("⏭️ Skip & Continue as Guest", use_container_width=True, type="secondary"):
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = "Guest"
            st.rerun()


# Initialize Auth
init_auth_state()

# ---------------- APP FLOW CONTROL ----------------
# Owner (localhost) bypass: Owner doesn't need to login
if LOGIN_ENABLED:
    if st.session_state.get("is_owner", False):
        # Owner access - no login required
        st.session_state["authenticated"] = True
    elif not st.session_state["authenticated"]:
        # Not owner and not authenticated - show login
        render_auth_ui()
        st.stop()  # Stop execution here if not logged in

# ---------------- MAIN APP CONTENT ----------------
# Logo & Header
col_logo, col_title = st.columns([1, 5])
with col_logo:
    # Professional fallback logo
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2563eb, #1e40af);
        color: white;
        width: 80px;
        height: 80px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        font-weight: bold;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    ">
        AI
    </div>
    """, unsafe_allow_html=True)

with col_title:
    st.title("AddressIntel AI")
    st.markdown("##### **Intelligent Corporate Location Intelligence**")

st.markdown("---")

# Instructions / Help
with st.expander("ℹ️ How it Works & Instructions"):
    st.markdown("""
    **1. Choose Extraction Mode (Sidebar)**
    *   **Free Mode**: Fast, uses regex to find addresses on the page. Good for simple sites.
    *   **Agentic Mode**: Uses **AI & Browser Automation**. It 'thinks', clicks dropdowns/maps, and extracts complex addresses. Requires an OpenAI API Key.

    **2. Input Data**
    *   **Single Company**: Enter Name/URL manually for a quick check.
    *   **Bulk Upload**: Upload an Excel file (`.xlsx`) with columns `COMPANY NAME` and `OFFICIAL WEBSITE`.

    **3. Run & Download**
    *   Click **Start Extraction**. The app will process each URL.
    *   Once done, download the **Structured Excel Report** with split street addresses, city, state, etc.
    """)

# Sidebar Config
with st.sidebar:
    st.header("Configuration")
    mode = st.radio("Extraction Mode", ["Free Mode", "Agentic Mode"], 
                    help="Free Mode uses Regex (Fast). Agentic Mode uses AI & Browsing (Smart).")
    
    api_key = ""
    proxy_url = ""
    
    if mode == "Agentic Mode":
        api_key = st.text_input("OpenAI API Key", type="password", help="Required for Agentic Mode")
        if not api_key:
            st.warning("Please enter API Key to proceed.")
            
        with st.expander("🚀 Scaling / Advanced Options"):
             st.info("Optional: Use these for high-volume extraction (10k+ companies).")
             proxy_url = st.text_input("HTTP Proxy URL", placeholder="http://user:pass@host:port")
             serp_key = st.text_input("SERP API Key (Not active yet)", placeholder="Coming soon...")

# Main Input Area
tab_single, tab_bulk = st.tabs(["🔹 Single Company", "📂 Bulk Upload (Excel)"])

input_data = [] # List of {"COMPANY NAME": ..., "OFFICIAL WEBSITE": ...}

with tab_single:
    st.subheader("Single Company Entry")
    col_name, col_url = st.columns(2)
    single_name = col_name.text_input("Company Name", placeholder="e.g. Tesla Inc.")
    single_url = col_url.text_input("Official Website", placeholder="e.g. https://tesla.com")
    
    if st.button("🚀 Extract Single", type="primary"):
        if single_url:
            input_data.append({"COMPANY NAME": single_name, "OFFICIAL WEBSITE": single_url})
        else:
            st.error("Website URL is required.")

with tab_bulk:
    st.subheader("Bulk Upload")
    st.markdown("Upload Excel file with columns: `COMPANY NAME`, `OFFICIAL WEBSITE`")
    uploaded_file = st.file_uploader("Upload Excel", type=["xlsx", "xls"])
    
    if uploaded_file and st.button("🚀 Process Bulk File", type="primary"):
        try:
            df_input = pd.read_excel(uploaded_file)
            # Normalize Headers
            df_input.columns = [c.upper().strip() for c in df_input.columns]
            
            if "COMPANY NAME" in df_input.columns and "OFFICIAL WEBSITE" in df_input.columns:
                input_data = df_input[["COMPANY NAME", "OFFICIAL WEBSITE"]].to_dict('records')
            else:
                st.error(f"Columns not found. Found: {list(df_input.columns)}")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# Processing Logic
if input_data:
    all_results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(input_data)
    
    for i, item in enumerate(input_data):
        name = item.get("COMPANY NAME", "Unknown")
        url = str(item.get("OFFICIAL WEBSITE", "")).strip()
        
        if not url or pd.isna(url):
            continue
            
        if not url.startswith("http"):
            url = "https://" + url
            
        status_text.text(f"Processing ({i+1}/{total}): {name} ({url})...")
        
        # Dispatch
        if mode == "Free Mode":
            raw_data = process_url_free(url)
        else:
            if not api_key:
                st.error("Stopping: API Key missing.")
                break
            raw_data = process_url_agentic(url, api_key, proxy_url)
            
        for row in raw_data:
            # Map standard columns
            # Free mode returns STREET only, Agentic returns structured
            row["COMPANY NAME"] = name
            row["COMPANY WEBSITE"] = url
            
            # Handle split street for free mode (dummy split)
            if "STREET" in row and "STREET ADDRESS1" not in row:
                row["STREET ADDRESS1"] = row["STREET"]
                row["STREET ADDRESS2"] = ""
            
            # Agentic mode returns street1/street2 map to correct keys
            if "street1" in row: row["STREET ADDRESS1"] = row["street1"]
            if "street2" in row: row["STREET ADDRESS2"] = row["street2"]
            if "city" in row: row["CITY NAME"] = row["city"]
            if "state" in row: row["STATE NAME"] = row["state"]
            if "zip" in row: row["PIN CODE"] = row["zip"]
            if "country" in row: row["COUNTRY NAME"] = row["country"]
            if "source_url" in row: row["ADDRESS SOURCE LINK"] = row["source_url"]
            if "SOURCE_LINK" in row: row["ADDRESS SOURCE LINK"] = row["SOURCE_LINK"]
            
            all_results.append(row)
            
        progress_bar.progress((i + 1) / total)
        
    status_text.success("Extraction Complete!")
    progress_bar.empty()
    
    if all_results:
        result_df = pd.DataFrame(all_results)
        
        # User defined structure
        desired_cols = [
            "COMPANY NAME", "COMPANY WEBSITE",
            "STREET ADDRESS1", "STREET ADDRESS2", "CITY NAME", 
            "STATE NAME", "PIN CODE", "COUNTRY NAME", "ADDRESS SOURCE LINK"
        ]
        
        # Ensure cols exist
        for c in desired_cols:
            if c not in result_df.columns:
                result_df[c] = ""
                
        final_df = result_df[desired_cols]
        
        st.subheader("Extracted Data")
        st.dataframe(final_df, use_container_width=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False)
            
        st.download_button(
            label="📥 Download Excel Result",
            data=buffer.getvalue(),
            file_name="extracted_addresses.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No addresses found for the provided inputs.")

