import time
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
# Sign up at scraperapi.com to get a free API key (1,000 requests free)
SCRAPER_API_KEY = "" #scraper key here

# Target Product URL (NeeDoh Ginger Glowman or equivalent target page)
TARGET_URL = "https://www.target.com/p/needoh-ginger-glowman/-/A-XXXXXXXX"

# Checking frequency (in seconds). Keep it reasonable to conserve API credits.
CHECK_INTERVAL = 120 

def check_stock_status():
    """Fetches the page content via ScraperAPI and checks inventory indicators."""
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': TARGET_URL,
        'render': 'true',  # Renders JavaScript content on the page
        'country': 'us'
    }
    
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking stock status...")
        response = requests.get('https://api.scraperapi.com/', params=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()

        # Target uses common keywords for out-of-stock items
        out_of_stock_keywords = [
            "out of stock", 
            "sold out", 
            "currently unavailable", 
            "temporarily out of stock"
        ]

        is_out_of_stock = any(keyword in page_text for keyword in out_of_stock_keywords)

        if not is_out_of_stock:
            return True  # Item appears to be in stock!
        else:
            print("Status: Out of Stock")
            return False

    except Exception as e:
        print(f"Error checking status: {e}")
        return False


def send_alert(message):
    """Sends a desktop notification or custom alert."""
    print("\n" + "="*50)
    print(f"🚨 IN-STOCK ALERT: {message}")
    print("="*50 + "\n")
    
    # Optional: Send SMS via Twilio or push notification via Pushover:
    # requests.post("https://api.pushover.net/1/messages.json", data={
    #     "token": "YOUR_PUSHOVER_APP_TOKEN",
    #     "user": "YOUR_PUSHOVER_USER_KEY",
    #     "message": message
    # })


def main():
    print("Starting Product Stock Monitor...")
    while True:
        in_stock = check_stock_status()
        
        if in_stock:
            send_alert(f"Target item is IN STOCK! Buy now: {TARGET_URL}")
            # Increase delay after positive alert to prevent spamming notifications
            time.sleep(300) 
        else:
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()