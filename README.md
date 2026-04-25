# ♻️ ScrapSync: Industrial Symbiosis & Automated Brokerage Console

![ScrapSync Banner](https://img.shields.io/badge/Status-Hackathon_Prototype-success) ![Python](https://img.shields.io/badge/Python-3.9+-blue.svg) ![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg) ![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E.svg) ![Stripe](https://img.shields.io/badge/Stripe-FPX_Gateway-6772E5.svg)

**ScrapSync** is an AI-powered B2B reverse-matchmaking platform designed to power the circular economy. It connects industrial manufacturers with local buyers and recyclers, transforming industrial waste (like untreated sawdust and copper wire) into profitable, reusable raw materials.

## ✨ Key Features

* 🧠 **AI Synergy Engine:** Upload single or batch PDF/image waste manifests. Gemini API instantly extracts visual text, calculates transport vs. material costs, and finds the most profitable local buyer.
* 💳 **Live FPX B2B Payments:** Fully integrated with the **Stripe API**, allowing users to execute digital twin smart contracts and process mock B2B banking transactions via Malaysian FPX gateways (Maybank2U, CIMB Clicks, etc.).
* 🔮 **Predictive Insights:** Forecasts weekly waste generation patterns, alerting factories to pre-optimize logistics and lock in regional market rates before seasonal oversupply drops prices.
* 📋 **Corporate Ledger:** An immutable, real-time transaction ledger powered by **Supabase PostgreSQL**.
* 🔐 **Enterprise Auth:** Secure hybrid registration allowing enterprises to act seamlessly as both buyers and sellers using Supabase Authentication.

## 🛠️ Technology Stack

* **Frontend UI:** Streamlit (Python)
* **Backend / Database:** Supabase (PostgreSQL, Authentication)
* **Payments Gateway:** Stripe Python SDK (FPX Test Environment)
* **AI/Computer Vision:** FastAPI Backend + AI extraction model (via `requests`)
* **Data Processing:** Pandas, NumPy

## 🚀 Installation & Setup

Follow these instructions to run the ScrapSync application on your local machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR-USERNAME/scrapsync.git](https://github.com/YOUR-USERNAME/scrapsync.git)
cd scrapsync

# 1. Setup
Run `pip install -r requirements.txt`.

# 2. How to run

1. Run `python backend/main.py`.
2. Then in new terminal, run `python -m streamlit run frontend/app.py`.
