import time
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
SCRAPER_API_KEY = "YOUR_SCRAPERAPI_KEY"
TARGET_URL = "https://www.target.com/p/needoh-ginger-glowman/-/A-XXXXXXXX"
CHECK_INTERVAL = 120  # Check every 2 minutes

# --- PUSHOVER CONFIGURATION ---
PUSHOVER_USER_KEY = "YOUR_PUSHOVER_USER_KEY"  # 30-character user key from dashboard
PUSHOVER_APP_TOKEN = "YOUR_PUSHOVER_APP_TOKEN"  # 30-character application API token


def check_stock_status():
    """Fetches page content via ScraperAPI and checks stock availability."""
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': TARGET_URL,
        'render': 'true',  # Required for JavaScript single-page app rendering
        'country': 'us'
    }
    
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking Target stock status...")
        # 70-second timeout accounts for headless browser execution
        response = requests.get('https://api.scraperapi.com/', params=payload, timeout=70)
        
        if response.status_code != 200:
            print(f"ScraperAPI returned HTTP status {response.status_code}")
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()

        out_of_stock_keywords = [
            "out of stock", 
            "sold out", 
            "currently unavailable", 
            "temporarily out of stock"
        ]

        is_out_of_stock = any(keyword in page_text for keyword in out_of_stock_keywords)
        return not is_out_of_stock

    except requests.exceptions.Timeout:
        print("⚠️ Warning: Request timed out waiting for ScraperAPI. Retrying on next check...")
        return False
    except Exception as e:
        print(f"Error checking status: {e}")
        return False


def send_pushover_alert(message_body):
    """Sends an instant push notification to your devices via Pushover."""
    url = "https://api.pushover.net/1/messages.json"
    payload = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": "🚨 Target In-Stock Alert!",
        "message": message_body,
        "url": TARGET_URL,
        "url_title": "Open Target Page",
        "sound": "magic"  # Optional alert sound (e.g., 'alien', 'cashregister', 'magic')
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        result = response.json()
        
        if result.get("status") == 1:
            print("\n🚨 Instant Pushover notification sent to your phone!\n")
        else:
            print(f"Failed to send Pushover alert: {result.get('errors')}")
    except Exception as e:
        print(f"Error sending Pushover notification: {e}")


def main():
    print("Starting Target Stock Monitor with Pushover...")
    
    # Optional startup check: send a test push notification when the script boots up
    send_pushover_alert("Stock monitor initialized and running successfully.")

    while True:
        in_stock = check_stock_status()
        
        if in_stock:
            alert_text = f"NeeDoh Ginger Glowman is back in stock!"
            send_pushover_alert(alert_text)
            # Sleep 10 minutes post-alert to prevent notification spam
            time.sleep(600)
        else:
            print("Status: Out of Stock")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()