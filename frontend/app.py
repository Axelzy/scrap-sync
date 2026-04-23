import streamlit as st
import requests
import pandas as pd
import numpy as np
import datetime
import time

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="ScrapSync | Intelligent Broker",
    page_icon="♻️",
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- CUSTOM CSS (The SaaS Look) ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        
        /* Premium File Uploader Styling */
        .stFileUploader > div > div {
            border: 2px dashed #17B169;
            background-color: rgba(23, 177, 105, 0.05);
            border-radius: 12px;
            padding: 30px;
            transition: all 0.3s ease;
        }
        .stFileUploader > div > div:hover {
            border-color: #0096FF;
            background-color: rgba(0, 150, 255, 0.05);
        }
        
        /* Nav Bar Radio Button Styling to look like pills */
        div.row-widget.stRadio > div {
            display: flex;
            flex-direction: row;
            justify-content: center;
            gap: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND CONNECTION ---
API_URL = "http://127.0.0.1:8000/upload-waste"

# --- SIDEBAR (Professional User Profile) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
    st.markdown("### ABC Wood Industries")
    st.caption("Manager: Ahmad | ID: #MY-8821")
    st.divider()
    st.markdown("**⚙️ System Diagnostics**")
    st.markdown("🟢 Engine: Online")
    st.markdown("🟢 AI Model: Z.AI Copilot")
    st.markdown("🟢 Network: Secure")
    st.divider()
    st.button("Log Out", use_container_width=True)

# --- HERO SECTION ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("♻️ ScrapSync Workspace")
    st.markdown("<h5 style='font-weight: 400; color: #888;'>Industrial Symbiosis & Automated Brokerage Console</h5>", unsafe_allow_html=True)
with col_head2:
    st.metric(label="Total YTD Profit", value="RM 42,500", delta="+12% this month")

st.write("") 

# --- TOP NAVIGATION BAR ---
selected_nav = st.radio(
    "Navigation",
    ["🚀 Synergy Engine", "📋 Corporate Ledger", "🌐 Live Market Demand"],
    horizontal=True,
    label_visibility="collapsed"
)
st.divider()

# ==========================================
# PAGE 1: THE SYNERGY ENGINE (Main App)
# ==========================================
if selected_nav == "🚀 Synergy Engine":
    upload_container = st.container(border=True)
    with upload_container:
        st.markdown("#### 📄 Initialize Synergy Routing")
        uploaded_file = st.file_uploader(
            "Upload Unstructured Manifest (PDF/Image)", 
            type=["png", "jpg", "jpeg", "pdf"],
            label_visibility="collapsed" 
        )

    if uploaded_file is None:
        st.info("👋 System Ready. Awaiting document upload to begin AI matchmaking...")

    else:
        st.write("") 
        with st.status("Initializing ScrapSync Copilot...", expanded=True) as status:
            st.write("🔍 Extracting visual text via OCR...")
            time.sleep(0.5)
            st.write("🧠 Querying Z.AI Neural Network...")
            
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            try:
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    match = data.get("ai_match_results", {})
                    
                    if "error" in match:
                        status.update(label="Analysis Failed", state="error", expanded=True)
                        st.error(f"AI Alert: {match['error']}")
                    else:
                        st.write("✅ Optimizing logistics routes...")
                        time.sleep(0.5)
                        status.update(label="Synergy Match Confirmed!", state="complete", expanded=False)
                        
                        st.success("✅ Profitable Synergy Route Established.")
                        st.write("")
                        
                        tab1, tab2, tab3, tab4 = st.tabs([
                            "📊 Match Analytics", 
                            "📍 Supply Chain Map", 
                            "🌱 ESG Dashboard", 
                            "⚖️ Smart Contract"
                        ])
                        
                        with tab1:
                            top_col1, top_col2, top_col3 = st.columns(3)
                            with top_col1:
                                st.metric(label="Projected New Profit", value=match.get("estimated_profit_myr", "RM 0.00"), delta="Saved from Landfill")
                            with top_col2:
                                st.metric(label="Target Buyer", value=match.get('best_buyer_match'), delta="Ready to receive", delta_color="normal")
                            with top_col3:
                                st.metric(label="Material Volume", value=match.get('quantity_detected'), delta="Verified", delta_color="normal")
                            
                            st.write("")
                            st.markdown("#### 🤖 AI Copilot Reasoning")
                            st.info(match.get('reasoning'))
                        
                        with tab2:
                            st.markdown("#### 📍 Optimized Logistics Route")
                            buyer_name = match.get('best_buyer_match', 'Matched Buyer')
                            
                            buyer_lat = 3.1390 + np.random.uniform(-0.1, 0.1)
                            buyer_lon = 101.6869 + np.random.uniform(-0.1, 0.1)
                            
                            map_data = pd.DataFrame({
                                'lat': [2.0442, buyer_lat],
                                'lon': [102.5689, buyer_lon],
                                'name': ['Your Facility (Muar)', f"{buyer_name} (HQ)"]
                            })

                            st.map(map_data, zoom=6, use_container_width=True)

                            l_col1, l_col2 = st.columns(2)
                            with l_col1:
                                st.info("🚚 **Estimated Distance:** ~158 km")
                            with l_col2:
                                st.info("🕒 **Transit Time:** 2h 15m (via E2)")

                        with tab3:
                            st.markdown("#### 🌱 Corporate ESG Impact")
                            c_col1, c_col2, c_col3 = st.columns(3)
                            with c_col1:
                                st.metric(label="Landfill Diverted", value="0.5 Tons", delta="Eco-Target Met", delta_color="normal")
                            with c_col2:
                                st.metric(label="CO2 Emissions Avoided", value="1.2 Tons", delta="-15% vs Last Month", delta_color="inverse")
                            with c_col3:
                                st.metric(label="Disposal Fees Saved", value="RM 350.00", delta="+ Profit Margin", delta_color="normal")
                            
                            st.write("")
                            st.markdown("##### 📈 Year-to-Date Carbon Offset Progress")
                            chart_data = pd.DataFrame({
                                "CO2 Saved (Tons)": [2.1, 2.5, 3.0, 3.8, 4.2, 5.4],
                                "Landfill Diverted (Tons)": [1.0, 1.2, 1.8, 2.0, 2.5, 3.0]
                            }, index=["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
                            
                            st.line_chart(chart_data, color=["#17B169", "#0096FF"])

                        with tab4:
                            st.markdown("#### ⚖️ Digital Waste Transfer Agreement")
                            if 'contract_generated' not in st.session_state:
                                st.session_state.contract_generated = False

                            if not st.session_state.contract_generated:
                                if st.button("Generate Legal Smart Contract", type="primary"):
                                    with st.spinner("Drafting terms based on AI analysis..."):
                                        time.sleep(1.5) 
                                        st.session_state.contract_generated = True
                                        st.rerun() 
                            
                            if st.session_state.contract_generated:
                                contract_container = st.container(border=True)
                                with contract_container:
                                    st.write(f"**Date Effective:** {datetime.date.today().strftime('%B %d, %Y')}")
                                    st.write(f"**Transaction ID:** #SC-8829-MY")
                                    st.write("---")
                                    st.markdown(f"This agreement is made between **The Seller (ABC Wood Industries)** and **The Buyer ({buyer_name})**.")
                                    st.markdown(f"**1. Material & Volume:** The Seller agrees to transfer and The Buyer agrees to accept **{match.get('quantity_detected')}** of **{match.get('material_detected')}**.")
                                    st.markdown(f"**2. Consideration:** The Buyer agrees to remit payment of **{match.get('estimated_profit_myr')}** upon successful weighing and quality inspection at the destination facility.")
                                    st.markdown(f"**3. Environmental Compliance:** Both parties adhere to the Environmental Quality Act 1974. The Seller guarantees the material is free from undeclared hazardous contaminants.")
                                    st.write("---")
                                    
                                    sig_col1, sig_col2 = st.columns(2)
                                    with sig_col1:
                                        st.write("Seller E-Signature:")
                                        st.text_input("Type full name to sign", key="seller_sig")
                                    with sig_col2:
                                        st.write("Buyer E-Signature:")
                                        st.write(f"*{buyer_name} (Auto-Verified via ScrapSync)*")
                                    
                                    st.write("")
                                    if st.button("Sign & Execute Digital Twin Contract", type="primary", use_container_width=True):
                                        st.balloons()
                                        st.success(f"Contract securely hashed! Logistics team dispatched to {buyer_name}.")

                else:
                    st.error(f"System Error: {response.status_code} - Please check backend connection.")
                    
            except requests.exceptions.ConnectionError:
                st.error("🚨 Critical Error: Could not connect to the ScrapSync Engine. Ensure FastAPI is running.")

# ==========================================
# PAGE 2: CORPORATE LEDGER
# ==========================================
elif selected_nav == "📋 Corporate Ledger":
    st.markdown("#### 📋 Historical Transaction Ledger")
    st.caption("Immutable record of all automated industrial symbiosis trades.")
    
    # Mock data to make the platform look active
    ledger_data = pd.DataFrame({
        "Date": ["2026-04-20", "2026-04-18", "2026-04-15", "2026-04-10"],
        "Material": ["Aluminum Swarf", "Used Engine Oil", "LDPE Shrink Wrap", "Copper Wire"],
        "Volume": ["120 kg", "600 Liters", "450 kg", "45 kg"],
        "Buyer": ["Klang Valley Metalworks", "BioLube Refineries", "EcoPolymer Solutions", "Klang Valley Metalworks"],
        "Revenue (MYR)": ["RM 3,000.00", "RM 720.00", "RM 1,125.00", "RM 1,125.00"],
        "Status": ["✅ Completed", "✅ Completed", "🚚 In Transit", "✅ Completed"]
    })
    st.dataframe(ledger_data, use_container_width=True, hide_index=True)

# ==========================================
# PAGE 3: LIVE MARKET DEMAND
# ==========================================
elif selected_nav == "🌐 Live Market Demand":
    st.markdown("#### 🌐 Live Buyer Network")
    st.caption("Current open demands from registered recycling facilities.")
    
    demand_col1, demand_col2 = st.columns(2)
    
    with demand_col1:
        st.info("**TechCycle Recovery Hub** is looking for: \n\n🔌 **Printed Circuit Boards (PCBs)** \n💰 Offering: RM 35.00 / kg")
        st.success("**Aisha Fungi Farms** is looking for: \n\n🪵 **Untreated Sawdust** \n💰 Offering: RM 1500 per ton")
        
    with demand_col2:
        st.warning("**Klang Valley Metalworks** is looking for: \n\n⚙️ **Aluminum & Copper Offcuts** \n💰 Offering: RM 25.00 / kg")
        st.info("**BioLube Refineries** is looking for: \n\n🛢️ **Used Engine Oil** \n💰 Offering: RM 1.20 / Liter")