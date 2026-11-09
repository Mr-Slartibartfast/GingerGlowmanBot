import time
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# --- CONFIGURATION ---
SCRAPER_API_KEY = ""
TARGET_URL = "https://www.target.com/p/needoh-ginger-glowman/-/A-XXXXXXXX"
CHECK_INTERVAL = 120  # Seconds between checks (2 minutes)

# --- TWILIO CONFIGURATION ---
# Find these credentials in your Twilio Console dashboard
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = "+"  # Your assigned Twilio virtual number
MY_PHONE_NUMBER = "+"      # Your personal cell phone number


def check_stock_status():
    """Fetches the page content via ScraperAPI and checks inventory indicators."""
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': TARGET_URL,
        'render': 'true',  # Renders JavaScript content
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


def send_sms_alert(message_body):
    """Sends an instant SMS alert via Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER
        )
        print(f"\n🚨 SMS Alert Sent Successfully! SID: {message.sid}\n")
    except Exception as e:
        print(f"Failed to send Twilio SMS: {e}")


def main():
    print("Starting Product Stock Monitor with Twilio SMS...")
    while True:
        in_stock = check_stock_status()
        
        if in_stock:
            alert_message = f"IN STOCK ALERT! Buy now: {TARGET_URL}"
            send_sms_alert(alert_message)
            # Sleep longer after a successful alert to prevent text spamming
            time.sleep(600) 
        else:
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()