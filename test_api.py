import requests

# Put your NEW key directly in here
API_KEY = "sk-d1db2964132eb763f108aca33d8997676e2c7c1ac7ecb2f8" 
API_URL = "https://api.ilmu.ai/v1/models"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

print("Querying ilmu.ai for allowed hackathon models...\n")

try:
    response = requests.get(API_URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! Here is the exact list of models you can use:")
        print("-" * 50)
        # Extract and print just the names of the models
        for model in data.get('data', []):
            print(f" 🤖 {model.get('id')}")
        print("-" * 50)
    else:
        print(f"❌ FAILED. Error {response.status_code}")
        print("Details:", response.text)

except Exception as e:
    print("\n❌ CRITICAL CRASH:", str(e))