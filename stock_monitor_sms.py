import time
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# --- CONFIGURATION ---
SCRAPER_API_KEY = ""
TARGET_URL = "https://www.target.com/p/needoh-ginger-glowman/-/A-XXXXXXXX"
CHECK_INTERVAL = 120  # Seconds between checks (2 minutes)

# --- EMAIL-TO-SMS CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "@gmail.com"
SENDER_PASSWORD = ""  # Your 16-character Google App Password


# Replace 1234567890 with your 10-digit phone number and match your carrier domain
RECIPIENT_SMS = "@txt.att.net" 


def check_stock_status():
    """Fetches page content via ScraperAPI and inspects inventory status."""
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': TARGET_URL,
        'render': 'true',  # Render JavaScript content
        'country': 'us'
    }
    
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking target inventory status...")
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
            return True  # Item is available!
        else:
            print("Status: Out of Stock")
            return False

    except Exception as e:
        print(f"Error checking status: {e}")
        return False


def send_free_sms_alert(message_body):
    """Sends a text message via your mobile carrier's free email gateway."""
    msg = MIMEText(message_body)
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_SMS
    msg["Subject"] = "Stock Alert"

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_SMS, msg.as_string())
        server.quit()
        print("\n🚨 Free SMS Alert Sent Successfully to Your Phone!\n")
    except Exception as e:
        print(f"Failed to send Email-to-SMS alert: {e}")


def main():
    print("Starting Product Stock Monitor (Email-to-SMS)...")
    while True:
        in_stock = check_stock_status()
        
        if in_stock:
            alert_text = f"Target item IN STOCK! Buy now: {TARGET_URL}"
            send_free_sms_alert(alert_text)
            # Pause 10 minutes post-alert to prevent notification flooding
            time.sleep(600) 
        else:
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()