import time
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
SCRAPER_API_KEY = ""
TARGET_URL = "https://www.target.com/p/needoh-ginger-glowman-fidget-toy/-/A-95271190"
CHECK_INTERVAL = 120  # Check every 2 minutes

# --- GMAIL SMTP CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "@gmail.com"
SENDER_PASSWORD = "wnrr qvuc ktie znlq"  # Google App Password

# List of email addresses to receive alerts
RECIPIENT_EMAILS = [
    "@gmail.com",
    "@gmail.com"
]


def check_stock_status():
    """Fetches page content via ScraperAPI and checks stock status."""
    payload = {
        'api_key': SCRAPER_API_KEY,
        'url': TARGET_URL,
        'render': 'true',  # Required for JavaScript single-page rendering
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


def send_email_alert(product_url):
    """Sends a formatted email alert to all recipients."""
    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENT_EMAILS)
    msg["Subject"] = "🚨 IN STOCK ALERT: NeeDoh Ginger Glowman"

    # HTML Body for clickability in standard mail clients
    html_content = f"""
    <html>
      <body>
        <h2>Target Stock Alert</h2>
        <p>The item you are monitoring is back in stock!</p>
        <p><a href="{product_url}" style="background-color:#CC0000; color:white; padding:10px 15px; text-decoration:none; border-radius:5px;">Buy Now on Target</a></p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, msg.as_string())
        server.quit()
        print(f"\n🚨 Email alert sent successfully to: {', '.join(RECIPIENT_EMAILS)}\n")
    except Exception as e:
        print(f"Failed to send email alert: {e}")


def main():
    print("Starting Target Stock Monitor with Email Notifications...")
    while True:
        in_stock = check_stock_status()
        
        if in_stock:
            send_email_alert(TARGET_URL)
            # Sleep 10 minutes post-alert to prevent notification spam
            time.sleep(600)
        else:
            print("Status: Out of Stock")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()