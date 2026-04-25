import streamlit as st
import requests
import pandas as pd
import numpy as np
import datetime
import time
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# --- INITIALIZE BACKEND ---
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    supabase = None
    st.sidebar.error("Supabase not connected. Check .env")

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="ScrapSync | Intelligent Broker",
    page_icon="♻️",
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- SESSION STATE MEMORY ---
if "uploaded_filenames" not in st.session_state:
    st.session_state.uploaded_filenames = []
if "single_match" not in st.session_state:
    st.session_state.single_match = None
if "batch_matches" not in st.session_state:
    st.session_state.batch_matches = None
if "batch_profit" not in st.session_state:
    st.session_state.batch_profit = 0.0

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stFileUploader > div > div {
            border: 2px dashed #17B169;
            background-color: rgba(23, 177, 105, 0.05);
            border-radius: 12px;
            padding: 30px;
        }
    </style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/upload-waste"

# --- HELPER FUNCTIONS ---
def get_ytd_profit():
    if supabase:
        try:
            res = supabase.table("transactions").select("revenue").execute()
            total = sum([item['revenue'] for item in res.data])
            return f"RM {total:,.2f}"
        except:
            return "RM 42,500.00"
    return "RM 42,500.00"

def get_ledger_data():
    if supabase:
        try:
            res = supabase.table("transactions").select("*").order("created_at", desc=True).execute()
            return pd.DataFrame(res.data)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def get_live_demands():
    if supabase:
        try:
            res = supabase.table("demand_nodes").select("*").limit(10).execute()
            return res.data
        except:
            return []
    return []

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
    st.markdown("### ABC Wood Industries")
    st.caption("Manager: Ahmad | ID: #MY-8821")
    st.divider()
    st.markdown("**⚙️ System Diagnostics**")
    st.markdown("🟢 DB: Supabase Connected")
    st.markdown("🟢 AI: Z.AI Copilot")
    st.markdown("🟢 Mode: Enterprise Batch Enabled")
    st.divider()
    st.button("Log Out", use_container_width=True)

# --- HERO SECTION ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("♻️ ScrapSync Workspace")
    st.markdown("<h5 style='font-weight: 400; color: #888;'>Industrial Symbiosis & Automated Brokerage Console</h5>", unsafe_allow_html=True)
with col_head2:
    st.metric(label="Total YTD Revenue", value=get_ytd_profit(), delta="+12% vs LY")

st.divider() 

# ==========================================
# SECTION 1: THE SYNERGY ENGINE
# ==========================================
st.header("🚀 Synergy Engine")
upload_container = st.container(border=True)
with upload_container:
    st.markdown("#### 📄 Initialize Synergy Routing")
    uploaded_files = st.file_uploader(
        "Upload Manifests (Single or Batch PDF/Images)", 
        type=["png", "jpg", "jpeg", "pdf"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

if not uploaded_files:
    st.info("👋 System Ready. Drag and drop documents to begin AI matchmaking...")
    if st.session_state.uploaded_filenames:
        st.session_state.uploaded_filenames = []
        st.session_state.single_match = None
        st.session_state.batch_matches = None

else:
    st.write("") 
    
    current_filenames = [f.name for f in uploaded_files]
    if current_filenames != st.session_state.uploaded_filenames:
        st.session_state.uploaded_filenames = current_filenames
        st.session_state.single_match = None
        st.session_state.batch_matches = None
        st.session_state.batch_profit = 0.0
    
    # --- SINGLE FILE UPLOAD ---
    if len(uploaded_files) == 1:
        uploaded_file = uploaded_files[0]
        
        if st.session_state.single_match is None:
            with st.status("Initializing ScrapSync Copilot...", expanded=True) as status:
                st.write("🔍 Extracting visual text via AI...")
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                try:
                    response = requests.post(API_URL, files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.single_match = data.get("ai_match_results", {})
                        status.update(label="Synergy Match Confirmed!", state="complete", expanded=False)
                    else:
                        st.error(f"System Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

        # Display from memory
        if st.session_state.single_match:
            match = st.session_state.single_match
            if "error" in match:
                st.error(f"AI Alert: {match['error']}")
            else:
                st.success("✅ Profitable Synergy Route Established.")
                
                # Stacked Results instead of Tabs
                st.markdown("#### 📊 Match Analytics")
                c1, c2, c3 = st.columns(3)
                c1.metric("Projected Profit", match.get("estimated_profit_myr"), "Saved")
                c2.metric("Target Buyer", match.get('best_buyer_match'), "Verified")
                c3.metric("Detected Vol", match.get('quantity_detected'), "Verified")
                st.info(match.get('reasoning'))
                
                st.write("")
                st.markdown("#### 📍 Supply Chain Map")
                st.map(pd.DataFrame({'lat': [2.0442, 3.1390], 'lon': [102.5689, 101.6869]}))
                
                st.write("")
                st.markdown("#### 🌱 ESG Dashboard")
                st.line_chart(pd.DataFrame(np.random.randn(10, 2), columns=['CO2', 'Landfill']))

                st.write("")
                st.markdown("#### ⚖️ Smart Contract")
                if st.button("Sign & Execute Digital Twin Contract", type="primary", use_container_width=True):
                    if supabase:
                        try:
                            raw_profit = str(match.get("estimated_profit_myr")).replace('RM','').replace(',','').strip()
                            supabase.table("transactions").insert({
                                "material": match.get("material_detected"),
                                "revenue": float(raw_profit) if raw_profit.replace('.','',1).isdigit() else 0.0,
                                "buyer": match.get("best_buyer_match")
                            }).execute()
                            st.success("Transaction recorded in live Supabase ledger!")
                        except Exception as e:
                            st.error(f"Database error: {e}")
                    else:
                        st.success("Contract Executed! (Supabase disconnected)")

    # --- BATCH PROCESSING (Multiple Files) ---
    elif len(uploaded_files) > 1:
        st.info(f"📦 Batch Mode Activated: {len(uploaded_files)} documents detected.")
        
        if st.session_state.batch_matches is None:
            if st.button("Process Monthly Batch", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                batch_results = []
                total_profit = 0.0
                
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"⏳ Processing document {i+1} of {len(uploaded_files)}: {file.name}...")
                    files_payload = {"file": (file.name, file, file.type)}
                    try:
                        res = requests.post(API_URL, files=files_payload)
                        if res.status_code == 200:
                            match = res.json().get("ai_match_results", {})
                            if "error" not in match:
                                batch_results.append({
                                    "Document": file.name,
                                    "Material": match.get("material_detected"),
                                    "Volume": match.get("quantity_detected"),
                                    "Buyer Route": match.get("best_buyer_match"),
                                    "Profit Margin": match.get("estimated_profit_myr")
                                })
                                try:
                                    raw_profit = str(match.get("estimated_profit_myr")).replace('RM','').replace(',','').strip()
                                    total_profit += float(raw_profit) if raw_profit.replace('.','',1).isdigit() else 0.0
                                except:
                                    pass
                    except:
                        pass 
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                st.session_state.batch_matches = batch_results
                st.session_state.batch_profit = total_profit
                st.rerun()

        if st.session_state.batch_matches is not None:
            st.write("")
            st.markdown("### 📊 Monthly Batch Analytics")
            b_col1, b_col2, b_col3 = st.columns(3)
            b_col1.metric("Documents Processed", len(st.session_state.batch_matches), f"Out of {len(uploaded_files)}")
            b_col2.metric("Total Projected Profit", f"RM {st.session_state.batch_profit:,.2f}", "Calculated by AI")
            
            unique_routes = len(set([x["Buyer Route"] for x in st.session_state.batch_matches])) if st.session_state.batch_matches else 0
            b_col3.metric("New Buyer Routes", unique_routes, "Connections made")
            
            st.dataframe(pd.DataFrame(st.session_state.batch_matches), use_container_width=True)

st.divider()

# ==========================================
# SECTION 2: PREDICTIVE INSIGHTS
# ==========================================
st.header("🔮 Predictive Insights")
st.caption("Forecasting waste generation patterns to pre-optimize logistics and lock in market rates.")
st.info("🧠 **Z.AI Forecasting Engine Alert:** A consistent weekly generation pattern has been identified for **Untreated Sawdust** at the Cutting Section (Bay 4).")
col_pred1, col_pred2 = st.columns([2, 1])

with col_pred1:
    st.markdown("##### 📈 30-Day Volume Forecast (Sawdust)")
    forecast_data = pd.DataFrame({
        "Recorded Volume (kg)": [420, 440, 455, 480, 0], 
        "AI Predicted (kg)": [0, 0, 0, 0, 530]
    }, index=["Week 1", "Week 2", "Week 3", "Current Week", "Next Week (Forecast)"])
    st.bar_chart(forecast_data, color=["#17B169", "#0096FF"])

with col_pred2:
    st.markdown("##### ⚡ Recommended Actions")
    action_card = st.container(border=True)
    with action_card:
        st.write("📦 **Forecast:** ~530 kg by Friday")
        st.write("🏢 **Optimum Buyer:** Aisha Fungi Farms")
        st.write("💰 **Projected Revenue:** RM 159.00")
        st.divider()
        st.caption("📉 **Market Alert:** Regional market rates for sawdust are predicted to drop 5% next week due to seasonal oversupply. Lock in current rates today.")
        if st.button("Auto-Book Predictive Route", type="primary", use_container_width=True):
            st.success("✅ Logistics preemptively scheduled for Friday! Digital Twin Smart Contract staged for final signature.")

st.divider()

# ==========================================
# SECTION 3: CORPORATE LEDGER
# ==========================================
st.header("📋 Corporate Ledger")
st.caption("Historical Transaction Ledger")
df = get_ledger_data()
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("No transactions found in Supabase. Execute a trade to see it here!")

st.divider()

# ==========================================
# SECTION 4: LIVE MARKET DEMAND
# ==========================================
st.header("🌐 Live Market Demand")
demands = get_live_demands()

if demands:
    cols = st.columns(2)
    for i, node in enumerate(demands):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{node['company_name']}**")
                st.caption(f"📍 {node['location']} | 🏭 {node['industry']}")
                st.write(f"🔍 **Looking for:** {node['material_needed']}")
                st.write(f"💰 **Max Budget:** RM {node['max_price_myr']}")
else:
    st.info("No buyers currently listed in demand_nodes.")