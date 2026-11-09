import time
import requests
from bs4 import BeautifulSoup
from plyer import notification

# --- CONFIGURATION ---
SCRAPER_API_KEY = ""
TARGET_URL = "https://www.target.com/p/needoh-ginger-glowman/-/A-XXXXXXXX"
CHECK_INTERVAL = 120  # Check every 2 minutes


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


def send_local_desktop_notification(message_body):
    """Triggers a native operating system pop-up banner on your desktop."""
    try:
        notification.notify(
            title="🚨 Target In-Stock Alert!",
            message=message_body,
            app_name="Stock Monitor Bot",
            timeout=10  # Duration in seconds the banner stays visible
        )
        print("\n🚨 Local desktop notification triggered successfully!\n")
    except Exception as e:
        print(f"Failed to trigger local notification: {e}")


def main():
    print("Starting Target Stock Monitor with Local Desktop Notifications...")
    
    # Startup check notification
    send_local_desktop_notification("Stock monitor script initialized successfully.")

    while True:
        in_stock = check_stock_status()
        
        if in_stock:
            alert_text = "NeeDoh Ginger Glowman is back in stock at Target!"
            send_local_desktop_notification(alert_text)
            # Sleep 10 minutes post-alert to prevent notification spam
            time.sleep(600)
        else:
            print("Status: Out of Stock")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()