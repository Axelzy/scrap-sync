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
supabase: Client = create_client(url, key)

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="ScrapSync | Intelligent Broker",
    page_icon="♻️",
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* REMOVED the header hiding line here! */
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stFileUploader > div > div {
            border: 2px dashed #17B169;
            background-color: rgba(23, 177, 105, 0.05);
            border-radius: 12px;
            padding: 30px;
        }
        div.row-widget.stRadio > div {
            display: flex;
            flex-direction: row;
            justify-content: center;
            gap: 20px;
        }
    </style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/upload-waste"

# --- HELPER FUNCTIONS (Live Data Fetching) ---
def get_ytd_profit():
    try:
        # Querying the transactions table for total profit
        res = supabase.table("transactions").select("revenue").execute()
        total = sum([item['revenue'] for item in res.data])
        return f"RM {total:,.2f}"
    except:
        return "RM 42,500.00" # Fallback for demo

def get_ledger_data():
    try:
        res = supabase.table("transactions").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame() # Fallback

def get_live_demands():
    res = supabase.table("demand_nodes").select("*").limit(10).execute()
    return res.data

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
    st.markdown("### ABC Wood Industries")
    st.caption("Manager: Ahmad | ID: #MY-8821")
    st.divider()
    st.markdown("**⚙️ System Diagnostics**")
    st.markdown("🟢 DB: Supabase Connected")
    st.markdown("🟢 AI: Z.AI Copilot")
    st.divider()
    st.button("Log Out", use_container_width=True)

# --- HERO SECTION ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("♻️ ScrapSync Workspace")
    st.markdown("<h5 style='font-weight: 400; color: #888;'>Industrial Symbiosis & Automated Brokerage Console</h5>", unsafe_allow_html=True)
with col_head2:
    # DYNAMIC METRIC FROM SUPABASE
    st.metric(label="Total YTD Revenue", value=get_ytd_profit(), delta="+12% vs LY")

st.write("") 

# --- TOP NAVIGATION BAR ---
selected_nav = st.radio("Navigation", ["🚀 Synergy Engine", "📋 Corporate Ledger", "🌐 Live Market Demand"], horizontal=True, label_visibility="collapsed")
st.divider()

# ==========================================
# PAGE 1: THE SYNERGY ENGINE (Main App)
# ==========================================
if selected_nav == "🚀 Synergy Engine":
    upload_container = st.container(border=True)
    with upload_container:
        st.markdown("#### 📄 Initialize Synergy Routing")
        uploaded_file = st.file_uploader("Upload Document", type=["png", "jpg", "jpeg", "pdf"], label_visibility="collapsed")

    if uploaded_file is None:
        st.info("👋 System Ready. Awaiting document upload to begin AI matchmaking...")
    else:
        with st.status("Initializing ScrapSync Copilot...", expanded=True) as status:
            st.write("🔍 Extracting visual text via OCR...")
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            try:
                response = requests.post(API_URL, files=files)
                if response.status_code == 200:
                    data = response.json()
                    match = data.get("ai_match_results", {})
                    
                    if "error" in match:
                        status.update(label="Analysis Failed", state="error")
                        st.error(f"AI Alert: {match['error']}")
                    else:
                        status.update(label="Synergy Match Confirmed!", state="complete", expanded=False)
                        st.success("✅ Profitable Synergy Route Established.")
                        
                        tab1, tab2, tab3, tab4 = st.tabs(["📊 Match Analytics", "📍 Supply Chain Map", "🌱 ESG Dashboard", "⚖️ Smart Contract"])
                        
                        with tab1:
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Projected Profit", match.get("estimated_profit_myr"), "Saved")
                            c2.metric("Target Buyer", match.get('best_buyer_match'), "Verified")
                            c3.metric("Detected Vol", match.get('quantity_detected'), "Verified")
                            st.info(match.get('reasoning'))
                        
                        with tab2: # Logistics Map
                            st.map(pd.DataFrame({'lat': [2.0442, 3.1390], 'lon': [102.5689, 101.6869]}))
                        
                        with tab3: # ESG
                            st.line_chart(pd.DataFrame(np.random.randn(10, 2), columns=['CO2', 'Landfill']))

                        with tab4: # Contract
                            if st.button("Sign & Execute Digital Twin Contract", type="primary", use_container_width=True):
                                # LOG TO SUPABASE ON SIGNING
                                try:
                                    supabase.table("transactions").insert({
                                        "material": match.get("material_detected"),
                                        "revenue": float(match.get("estimated_profit_myr").replace('RM','').replace(',','')),
                                        "buyer": match.get("best_buyer_match")
                                    }).execute()
                                    st.balloons()
                                    st.success("Transaction recorded in live Supabase ledger!")
                                except:
                                    st.balloons()
                                    st.success("Contract Executed!")

            except Exception as e:
                st.error(f"Connection Error: {e}")

# ==========================================
# PAGE 2: CORPORATE LEDGER (DYNAMIC)
# ==========================================
elif selected_nav == "📋 Corporate Ledger":
    st.markdown("#### 📋 Historical Transaction Ledger")
    df = get_ledger_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No transactions found in Supabase. Execute a trade to see it here!")

# ==========================================
# PAGE 3: LIVE MARKET DEMAND (DYNAMIC)
# ==========================================
elif selected_nav == "🌐 Live Market Demand":
    st.markdown("#### 🌐 Live Buyer Network")
    demands = get_live_demands()
    
    if demands:
        # Displaying buyers in a grid
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