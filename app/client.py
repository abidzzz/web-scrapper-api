import requests
import time

# Replace with your local server URL if different
BASE_URL = "http://127.0.0.1:5000"

def start_search(query):
    response = requests.get(f"{BASE_URL}/search", params={"q": query})
    if response.status_code == 200:
        return response.json().get('task_id')
    else:
        print("Error starting search:", response.json())
        return None

def check_status(task_id):
    response = requests.get(f"{BASE_URL}/status/{task_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error checking status:", response.json())
        return None

def main():
    query = "Adidas men shoes"  # Replace with your search query
    task_id = start_search(query)

    if not task_id:
        print("Failed to start search task.")
        return

    print(f"Search started. Task ID: {task_id}")

    while True:
        status = check_status(task_id)
        if status['status'] == 'completed':
            print("Search completed. Results:")
            for result in status['result']:
                print(result)
            break
        else:
            t = 15
            print(f"Search in progress, checking again in {t} seconds...")
            time.sleep(t)

if __name__ == "__main__":
    main()