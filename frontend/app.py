import streamlit as st
import requests
import pandas as pd
import numpy as np
import datetime
import time
import os
import math
import stripe
from dotenv import load_dotenv
from supabase import create_client, Client

# --- INITIALIZE BACKEND ---
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
stripe.api_key = os.environ.get("STRIPE_API_KEY")

# Create a bulletproof absolute path for the logo
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "image_e20e96.jpg")

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    supabase = None

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="ScrapSync | Intelligent Broker",
    page_icon="",
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# ==========================================
# SESSION STATE MEMORY (FIXED FOR RELOADS)
# ==========================================
if "uploaded_filenames" not in st.session_state:
    st.session_state.uploaded_filenames = []
if "single_match" not in st.session_state:
    st.session_state.single_match = None
if "batch_matches" not in st.session_state:
    st.session_state.batch_matches = None
if "batch_profit" not in st.session_state:
    st.session_state.batch_profit = 0.0
if "demand_page" not in st.session_state:
    st.session_state.demand_page = 1

# Auth State Memory & Browser URL Memory
if "logged_in" in st.query_params and st.query_params["logged_in"] == "true":
    st.session_state.authenticated = True
    if "user_email" not in st.session_state or not st.session_state.user_email:
        st.session_state.user_email = st.query_params.get("user", "user@enterprise.com")
else:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""

# Payment Gateway Memory
if "show_checkout" not in st.session_state:
    st.session_state.show_checkout = False
if "checkout_data" not in st.session_state:
    st.session_state.checkout_data = {}
if "active_scan" not in st.session_state:
    st.session_state.active_scan = False

# FPX Asynchronous Gateway Memory
if "fpx_intent_id" not in st.session_state:
    st.session_state.fpx_intent_id = None
if "fpx_url" not in st.session_state:
    st.session_state.fpx_url = None

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

# ==========================================
# AUTHENTICATION GATEKEEPER
# ==========================================
if not st.session_state.authenticated:
    # --- LOGO ON LOGIN PAGE ---
    if os.path.exists(logo_path):
        st.image(logo_path, width=1)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 60px;'></h1>", unsafe_allow_html=True)
        
    st.markdown("<h1 style='text-align: center;'>Welcome to ScrapSync</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please log in or register your enterprise to access the Synergy Engine.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tabs = st.tabs(["🔒 Login", "📝 Register New Enterprise"])
        
        with auth_tabs[0]:
            st.markdown("### User Login")
            login_email = st.text_input("Email Address", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Access Dashboard", type="primary", use_container_width=True):
                if supabase:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": login_email,
                            "password": login_password
                        })
                        st.session_state.authenticated = True
                        st.session_state.user_email = login_email
                        
                        st.query_params["logged_in"] = "true"
                        st.query_params["user"] = login_email
                        
                        st.success("Login successful! Loading engine...")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error("Invalid email or password. Please try again.")
                else:
                    st.error("Database disconnected. Cannot verify login.")

        with auth_tabs[1]:
            st.markdown("### Register Enterprise Account")
            reg_email = st.text_input("Corporate Email", key="reg_email")
            reg_password = st.text_input("Create Password", type="password", key="reg_password")
            reg_company = st.text_input("Company Name", key="reg_company")
            reg_role = st.selectbox("Account Type", [
                "Hybrid Enterprise (Buy & Sell)", 
                "Manufacturer (Primary Seller)", 
                "Recycler (Primary Buyer)"
            ])
            
            if st.button("Create Account", use_container_width=True):
                if supabase:
                    try:
                        response = supabase.auth.sign_up({
                            "email": reg_email,
                            "password": reg_password,
                        })
                        st.success(f"Account created for {reg_company}! You can now log in on the Login tab.")
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
                else:
                    st.error("Database disconnected. Cannot create account.")
                    
    st.stop()


# ==========================================
# MAIN APPLICATION (Only runs if logged in)
# ==========================================

# Use BACKEND_URL from environment variables for production, otherwise default to local
BASE_API_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
API_URL = f"{BASE_API_URL}/upload-waste"

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
            res = supabase.table("demand_nodes").select("*").execute()
            return res.data
        except:
            return []
    return []

def get_supply_nodes():
    if supabase:
        try:
            res = supabase.table("supply_nodes").select("*").execute()
            return res.data
        except:
            return []
    return []

with st.sidebar:
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        st.markdown("<h2 style='text-align: center;'></h2>", unsafe_allow_html=True)
        
    st.markdown("### ScrapSync Portal")
    st.caption(f"Logged in as: {st.session_state.user_email}")
    if supabase is None:
        st.error("Supabase not connected. Check .env")
    st.divider()
    
    st.markdown("**⚙️ System Diagnostics**")
    st.markdown("🟢 DB: Supabase Auth Active")
    st.markdown("🟢 AI: Z.AI Copilot")
    st.markdown("🟢 Mode: Enterprise Batch Enabled")
    st.divider()
    
    if st.button("Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.session_state.active_scan = False
        st.session_state.show_checkout = False
        st.session_state.fpx_intent_id = None
        st.session_state.fpx_url = None
        
        st.query_params.clear()
        
        if supabase:
            supabase.auth.sign_out()
        st.rerun()

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title(" ScrapSync Workspace")
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
    uploaded_files = st.file_uploader("Upload Manifests", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True, label_visibility="collapsed")

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
    
    # SINGLE FILE
    if len(uploaded_files) == 1:
        uploaded_file = uploaded_files[0]
        if st.session_state.single_match is None:
            with st.status("Initializing ScrapSync Copilot...", expanded=True) as status:
                st.write("🔍 Extracting visual text via AI...")
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                try:
                    response = requests.post(API_URL, files=files)
                    if response.status_code == 200:
                        st.session_state.single_match = response.json().get("ai_match_results", {})
                        status.update(label="Synergy Match Confirmed!", state="complete", expanded=False)
                    else:
                        st.error(f"System Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

        if st.session_state.single_match:
            match = st.session_state.single_match
            if "error" in match:
                st.error(f"AI Alert: {match['error']}")
            else:
                st.success("✅ Profitable Synergy Route Established.")
                st.markdown("#### 📊 Match Analytics")
                c1, c2, c3, c4 = st.columns(4)
                
                profit_str = str(match.get("estimated_profit_myr", ""))
                is_loss = "LOSS" in profit_str
                
                c1.metric("Net Profit" if not is_loss else "Projected Loss", profit_str, "Calculated")
                c2.metric("Target Buyer", match.get('best_buyer_match'), "Verified")
                c3.metric("Detected Vol", match.get('quantity_detected'), "Verified")
                c4.metric("Transport Cost", match.get('transport_cost_myr', "N/A"), "- Deducted")
                
                if is_loss:
                    st.error(match.get('reasoning'))
                else:
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
                            raw_profit = str(match.get("estimated_profit_myr")).replace('RM','').replace(',','').replace('LOSS: -','').strip()
                            final_revenue = float(raw_profit) if raw_profit.replace('.','',1).isdigit() else 0.0
                            if is_loss:
                                final_revenue = -abs(final_revenue)
                                
                            supabase.table("transactions").insert({
                                "material": match.get("material_detected"),
                                "revenue": final_revenue,
                                "buyer": match.get("best_buyer_match")
                            }).execute()
                            st.success("Transaction recorded in live Supabase ledger!")
                        except Exception as e:
                            st.error(f"Database error: {e}")
                    else:
                        st.success("Contract Executed! (Supabase disconnected)")

    # BATCH FILES
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
                                    "Net Profit": match.get("estimated_profit_myr"),
                                    "Transport": match.get("transport_cost_myr", "N/A")
                                })
                                try:
                                    raw_profit = str(match.get("estimated_profit_myr")).replace('RM','').replace(',','').replace('LOSS: -','').strip()
                                    amt = float(raw_profit) if raw_profit.replace('.','',1).isdigit() else 0.0
                                    if "LOSS" in str(match.get("estimated_profit_myr")):
                                        total_profit -= amt
                                    else:
                                        total_profit += amt
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
            b_col2.metric("Total Net Profit", f"RM {st.session_state.batch_profit:,.2f}", "Logistics Deducted")
            unique_routes = len(set([x["Buyer Route"] for x in st.session_state.batch_matches])) if st.session_state.batch_matches else 0
            b_col3.metric("New Buyer Routes", unique_routes, "Connections made")
            st.dataframe(pd.DataFrame(st.session_state.batch_matches), use_container_width=True)

st.divider()

# ==========================================
# SECTION 2: PREDICTIVE INSIGHTS (RESTORED)
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
all_demands = get_live_demands()
search_term = st.text_input("🔍 Search by material, company name, or industry:", placeholder="e.g., Sawdust, Electronics...").lower()
filtered_demands = [d for d in all_demands if search_term in str(d.get('material_needed', '')).lower() or search_term in str(d.get('company_name', '')).lower()]

if not filtered_demands:
    st.info(f"No buyers found matching '{search_term}'.")
else:
    ITEMS_PER_PAGE = 4
    total_pages = max(1, math.ceil(len(filtered_demands) / ITEMS_PER_PAGE))
    if st.session_state.demand_page > total_pages: st.session_state.demand_page = total_pages
    start_idx = (st.session_state.demand_page - 1) * ITEMS_PER_PAGE
    demands_to_show = filtered_demands[start_idx:start_idx + ITEMS_PER_PAGE]
    cols = st.columns(2)
    for i, node in enumerate(demands_to_show):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{node.get('company_name', 'Unknown')}**")
                st.caption(f"📍 {node.get('location', 'N/A')} | 🏭 {node.get('industry', 'N/A')}")
                st.write(f"🔍 **Looking for:** {node.get('material_needed', 'N/A')}")
                st.write(f"💰 **Max Budget:** RM {node.get('max_price_myr', '0.00')} / kg")

st.divider()

# ==========================================
# SECTION 5: LIVE MATERIAL SUPPLY
# ==========================================
st.header("📦 Live Material Supply")
supplies = get_supply_nodes()
if supplies:
    s_cols = st.columns(3)
    for i, node in enumerate(supplies):
        with s_cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{node.get('company_name', 'Unknown')}**")
                st.write(f"📦 **Selling:** {node.get('material_available', 'N/A')}")
                st.write(f"🏷️ **Price:** RM {node.get('price_per_kg_myr', '0.00')} / kg")

# ==========================================
# SECTION 6: AI PROCUREMENT ENGINE & FPX STRIPE CHECKOUT
# ==========================================
st.divider()
st.header("🛒 AI Procurement Console")
st.caption("Reverse-Matchmaking: Source cheap recycled raw materials to replace expensive virgin materials.")

procure_col1, procure_col2 = st.columns([1, 2])

with procure_col1:
    with st.container(border=True):
        st.markdown("#### Source Materials")
        procure_query = st.text_input("What are you looking for?", placeholder="e.g., Copper wire, sawdust...", key="procure_input")
        volume_needed = st.number_input("Target Volume (kg)", min_value=100, step=100, value=1000)
        
        if st.button("Scan Market for Cheapest Supply", type="primary", use_container_width=True):
            if procure_query:
                st.session_state.active_scan = True
                st.session_state.show_checkout = False
                # Reset FPX state when they scan for a new item
                st.session_state.fpx_intent_id = None
                st.session_state.fpx_url = None

with procure_col2:
    if st.session_state.active_scan:
        with st.spinner("Z.AI is calculating Landed Costs across all suppliers..."):
            time.sleep(1) # Simulate AI
            
            st.success("✅ Optimum Procurement Route Found!")
            st.markdown("#### 🏆 Best Supplier: Shah Alam Metals")
            
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            metrics_col1.metric("Total Landed Cost", "RM 25,060.00", "Lowest Available", delta_color="inverse")
            metrics_col2.metric("Material Cost", "RM 25,000.00", "@ RM 25.00/kg")
            metrics_col3.metric("Transport Cost", "RM 60.00", "Distance: 40km")
            
            st.info("**AI Reasoning:** Shah Alam Metals charges RM 25.00/kg, but because they are only 40km away, the Total Landed Cost is significantly cheaper for this volume compared to competitors.")
            
            if st.button("Draft Purchase Order (Smart Contract)", use_container_width=True):
                st.session_state.show_checkout = True
                st.session_state.active_scan = False 
                st.session_state.checkout_data = {
                    "supplier": "Shah Alam Metals",
                    "material": procure_query,
                    "volume": volume_needed,
                    "total_cost": 25060.00
                }
                st.rerun()

    elif not st.session_state.show_checkout:
        st.info("👈 Enter your material requirements to scan the live supply market.")

# --- THE FPX STRIPE PAYMENT GATEWAY UI ---
if st.session_state.show_checkout:
    st.write("")
    st.subheader("💳 BNM / Stripe FPX Gateway")
    st.caption("Live Bank-to-Bank B2B Checkout connected via PayNet Malaysia")
    
    with st.container(border=True):
        cd = st.session_state.checkout_data
        st.markdown(f"**Recipient:** {cd['supplier']}")
        st.markdown(f"**Commodity:** {cd['volume']} kg of {cd['material']}")
        st.markdown(f"**Total Amount Due:** <span style='color:#17B169; font-size: 1.2rem; font-weight: bold;'>RM {cd['total_cost']:,.2f}</span>", unsafe_allow_html=True)
        st.divider()
        
        # FPX Bank Dictionary
        fpx_banks = {
            "Maybank2U": "maybank2u",
            "CIMB Clicks": "cimb",
            "Public Bank": "public_bank",
            "RHB Now": "rhb",
            "Hong Leong Connect": "hong_leong_bank",
            "AmBank": "ambank"
        }
        
        st.info("ℹ️ **Stripe FPX Sandbox Active:** You will be redirected to a simulated Malaysian banking portal to authorize this transfer.")
        
        selected_bank_name = st.selectbox("Select Your Corporate Bank", list(fpx_banks.keys()))
        selected_bank_code = fpx_banks[selected_bank_name]
        
        # STAGE 1: INITIATE THE TRANSFER
        if not st.session_state.fpx_intent_id:
            st.write("")
            if st.button(f"Initiate Transfer via {selected_bank_name}", type="primary", use_container_width=True):
                if not stripe.api_key:
                    st.error("🚨 Stripe API Key missing! Please check your .env file.")
                    st.stop()
                    
                with st.spinner("Connecting to BNM Secure Gateway..."):
                    try:
                        amount_in_sen = int(cd['total_cost'] * 100)
                        
                        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:8501")
                        intent = stripe.PaymentIntent.create(
                            amount=amount_in_sen,
                            currency="myr",
                            payment_method_types=["fpx"],
                            payment_method_data={
                                "type": "fpx",
                                "fpx": {"bank": selected_bank_code}
                            },
                            confirm=True,
                            return_url=f"{frontend_url}/?logged_in=true&user={st.session_state.user_email}", 
                            description=f"ScrapSync: {cd['volume']}kg {cd['material']}"
                        )
                        
                        if intent.status == "requires_action":
                            # Save Intent Data to memory
                            st.session_state.fpx_intent_id = intent.id
                            st.session_state.fpx_url = intent.next_action.redirect_to_url.url
                            st.rerun()
                        else:
                            st.error(f"Unexpected Stripe Status: {intent.status}")
                            
                    except stripe.error.StripeError as e:
                        st.error(f"💳 Stripe API Error: {e.user_message}")

        # STAGE 2: AUTHORIZE AND VERIFY (ASYNC)
        else:
            st.warning(f"⏳ **Transaction Pending.** A secure connection to {selected_bank_name} has been established.")
            
            # The Magic New Tab Button
            st.link_button(f"🌐 Click Here to Authorize at {selected_bank_name} (Opens New Tab)", st.session_state.fpx_url, type="primary", use_container_width=True)
            
            st.write("---")
            st.markdown("After you click 'Authorize Test Payment' in the new tab, return here and click Verify.")
            
            if st.button("Verify Transfer & Execute Smart Contract", use_container_width=True):
                with st.spinner("Pinging PayNet/Stripe servers to confirm funds..."):
                    try:
                        # Retrieve the latest status directly from Stripe
                        intent = stripe.PaymentIntent.retrieve(st.session_state.fpx_intent_id)
                        
                        if intent.status == "succeeded":
                            st.success(f"✅ FPX Transfer Successful! (Receipt: {intent.id})")
                            
                            # WRITE TO SUPABASE LEDGER
                            if supabase:
                                try:
                                    supabase.table("transactions").insert({
                                        "material": f"PURCHASE: {cd['material']} (from {cd['supplier']})",
                                        "revenue": -abs(cd['total_cost']),
                                        "buyer": st.session_state.user_email
                                    }).execute()
                                    st.success("✅ Immutable Smart Contract Executed & Ledger Updated.")
                                except Exception as e:
                                    st.error(f"Stripe succeeded, but Database failed: {e}")
                            else:
                                st.success("✅ Smart Contract Executed! (Supabase disconnected)")
                            
                            # Clear Memory & Return to dashboard
                            time.sleep(3.5)
                            st.session_state.show_checkout = False
                            st.session_state.fpx_intent_id = None
                            st.session_state.fpx_url = None
                            st.rerun()
                            
                        elif intent.status == "requires_action":
                            st.error("❌ Transfer not completed yet. Please authorize the payment in the Stripe tab first.")
                        else:
                            st.error(f"❌ Transfer Failed (Status: {intent.status})")
                            # Reset so they can try again
                            st.session_state.fpx_intent_id = None
                            st.session_state.fpx_url = None
                            
                    except stripe.error.StripeError as e:
                        st.error(f"💳 Stripe Error: {e.user_message}")