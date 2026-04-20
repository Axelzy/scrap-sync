import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load the hidden API keys from the .env file
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initializes the connection to Supabase securely."""
        self.url: str = os.environ.get("SUPABASE_URL")
        self.key: str = os.environ.get("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Database credentials missing! Check your .env file.")
            
        self.client: Client = create_client(self.url, self.key)

    def fetch_all_buyers(self):
        """Retrieves all 'Demand Nodes' (buyers) from the database."""
        try:
            response = self.client.table("demand_nodes").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching buyers: {e}")
            return None

# --- TEST THE CONNECTION ---
if __name__ == "__main__":
    print("Connecting to the ScrapSync Database...") # <-- Updated Name!
    db = DatabaseManager()
    buyers = db.fetch_all_buyers()
    
    if buyers:
        print("\n✅ SCRAPSYNC CONNECTION SUCCESSFUL! Found these buyers:") # <-- Updated Name!
        for b in buyers:
            print(f"- {b['company_name']} (Needs: {b['material_needed']} | Budget: RM{b['max_price_myr']})")
    else:
        print("\n❌ Failed to retrieve data. Check your Supabase connection.")