import time
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
SCRAPER_API_KEY = "YOUR_SCRAPERAPI_KEY"
TARGET_URL = "https://www.target.com/p/needoh-ginger-glowman/-/A-XXXXXXXX"
CHECK_INTERVAL = 120  # Check every 2 minutes

# --- DISCORD CONFIGURATION ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE"


def check_stock_status():
    """Fetches page content via ScraperAPI and checks stock availability."""
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': TARGET_URL,
        'render': 'true',  # Render JS single-page app components
        'country': 'us'
    }
    
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking Target stock status...")
        # 70-second timeout accounts for headless browser rendering
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


def send_discord_alert(message_body):
    """Sends a formatted embed notification to your Discord server."""
    # Rich embed formatting for clear readability on mobile
    embed_payload = {
        "username": "Stock Monitor Bot",
        "embeds": [
            {
                "title": "🚨 IN STOCK ALERT!",
                "description": message_body,
                "url": TARGET_URL,
                "color": 5763719,  # Green color (#57F287)
                "footer": {
                    "text": "Target Stock Monitoring System"
                }
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=embed_payload, timeout=10)
        if response.status_code == 204:
            print("\n🚨 Instant alert sent successfully to Discord!\n")
        else:
            print(f"Failed to send Discord alert: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error sending Discord alert: {e}")


def main():
    print("Starting Target Stock Monitor with Discord Webhooks...")
    
    # Startup check to verify your webhook is connected properly
    send_discord_alert("Stock monitor initialized and actively checking Target inventory.")

    while True:
        in_stock = check_stock_status()
        
        if in_stock:
            alert_text = f"**NeeDoh Ginger Glowman** is back in stock at Target!\n\n[Click here to buy now]({TARGET_URL})"
            send_discord_alert(alert_text)
            # Sleep 10 minutes post-alert to prevent channel spam
            time.sleep(600)
        else:
            print("Status: Out of Stock")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()