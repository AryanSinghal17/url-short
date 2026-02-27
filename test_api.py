import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_tests():
    print("--- Starting API Tests ---")
    
    # 1. Get initial URLs
    res = requests.get(f"{BASE_URL}/urls")
    print("Initial GET /urls:", res.status_code, res.json())
    
    # 2. Create a short URL
    payload = {"original_url": "https://www.google.com"}
    res = requests.post(f"{BASE_URL}/shorten", json=payload)
    print("POST /shorten status:", res.status_code)
    
    if res.status_code != 201:
        print("Failed to create URL:", res.text)
        return
        
    data = res.json()
    print("POST /shorten response:", data)
    short_code = data["short_code"]
    
    # 3. Test Redirect (allow_redirects=False to check the 307 status)
    res = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
    print(f"GET /{short_code} status:", res.status_code)
    print(f"Redirect Location:", res.headers.get("location"))
    
    # Wait a moment for async db update (click count)
    time.sleep(1)
    
    # 4. Get URLs again to check click count
    res = requests.get(f"{BASE_URL}/urls")
    print("GET /urls after redirect:", json.dumps(res.json(), indent=2))
    
    # 5. Delete the URL
    res = requests.delete(f"{BASE_URL}/{short_code}")
    print(f"DELETE /{short_code} status:", res.status_code)
    
    # 6. Verify Deletion
    res = requests.get(f"{BASE_URL}/urls")
    print("GET /urls after delete:", json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print("Error during tests:", str(e))
