import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_endpoint(endpoint):
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"Testing {url}...")
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            if 'dashboard' in data:
                print(f"Dashboard Keys: {list(data['dashboard'].keys())}")
                print(f"Total Expenses: {data['dashboard'].get('total_expenses')}")
            elif 'expenses' in data:
                print(f"Expenses Count: {len(data['expenses'])}")
            print("-" * 20)
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_endpoint('/dashboard')
    test_endpoint('/expenses')
