import streamlit as st
import requests

# --- UI CONFIGURATION ---
st.set_page_config(
    page_title="ScrapSync | Intelligent Broker",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="collapsed" # Keeps the UI ultra-clean by default
)

# --- CUSTOM CSS (The SaaS Look) ---
# This hides the Streamlit watermarks and tightens up the padding
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        /* Make the upload box look more clickable and professional */
        .stFileUploader > div > div {
            border: 2px dashed #4CAF50;
            border-radius: 10px;
            padding: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND CONNECTION ---
API_URL = "http://127.0.0.1:8000/upload-waste"

# --- HERO SECTION ---
# Centered text for a modern landing page feel
st.markdown("<h1 style='text-align: center;'>♻️ ScrapSync</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; font-weight: 400; color: #555;'>The AI-Powered Industrial Symbiosis Broker</h4>", unsafe_allow_html=True)
st.write("") # Spacer

# --- MAIN DASHBOARD ---
upload_container = st.container(border=True)

with upload_container:
    st.markdown("### 📄 Initialize Synergy")
    st.caption("Upload unstructured waste manifests, handwritten logs, or PDF safety sheets.")
    
    uploaded_file = st.file_uploader(
        "Upload Document", 
        type=["png", "jpg", "jpeg", "pdf"],
        label_visibility="hidden" # Hides the default label for a cleaner look
    )

# --- PROCESSING & RESULTS ---
if uploaded_file is None:
    # Empty State UX
    st.info("👋 Awaiting document upload to begin AI matchmaking...")

else:
    st.write("") # Spacer
    with st.spinner("🧠 Z.AI Copilot is analyzing document and querying the market..."):
        
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        
        try:
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                data = response.json()
                match = data.get("ai_match_results", {})
                
                if "error" in match:
                    st.error(f"AI Alert: {match['error']}")
                else:
                    # --- THE RESULTS CARDS ---
                    st.success("✅ Profitable Synergy Confirmed")
                    
                    # Highlight the primary value proposition instantly
                    st.metric(
                        label="Projected New Profit", 
                        value=match.get("estimated_profit_myr", "RM 0.00"), 
                        delta="Saved from Landfill Disposal Fees"
                    )
                    
                    # Use a container to group the transaction details cleanly
                    details_card = st.container(border=True)
                    with details_card:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📦 Discovered Supply**")
                            st.write(f"**Material:** {match.get('material_detected')}")
                            st.write(f"**Volume:** {match.get('quantity_detected')}")
                            
                        with col2:
                            st.markdown("**🏢 Optimum Buyer Match**")
                            st.write(f"**Company:** {match.get('best_buyer_match')}")
                            st.write("**Status:** Ready to receive")

                    # Keep the reasoning separated and highly readable
                    st.markdown("#### 🤖 Copilot Reasoning")
                    st.info(match.get('reasoning'))
                    
                    st.write("") # Spacer
                    
                    # Call to Action
                    if st.button("Execute Trade & Automate Introduction", use_container_width=True, type="primary"):
                        st.balloons()
                        st.success(f"Legal and logistical introduction drafted and sent to {match.get('best_buyer_match')}!")

            else:
                st.error(f"System Error: {response.status_code} - Please check backend connection.")
                
        except requests.exceptions.ConnectionError:
            st.error("🚨 Critical Error: Could not connect to the ScrapSync Engine. Ensure FastAPI is running.")

# --- MINIMAL SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ System Status")
    st.markdown("🟢 **API Engine:** Online")
    st.markdown("🟢 **Z.AI GLM-4:** Online")
    st.markdown("🟢 **OCR Subsystem:** Online")
    st.divider()
    st.caption("ScrapSync Prototype v1.0")