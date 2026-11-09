import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import threading
import time
import webbrowser

# --- CONFIGURATION ---
SCRAPER_API_KEY = "scraperKeyHere"  # Insert your ScraperAPI Key here
CHECK_INTERVAL_SECONDS = 300            # Check every 5 minutes

class TargetStockWidget(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Target Stock Monitor")
        self.geometry("400x310")
        self.resizable(False, False)
        self.attributes("-topmost", True)  # Keeps widget floating on desktop

        # Dark theme styling
        self.configure(bg="#1e1e1e")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        # Header
        self.lbl_title = tk.Label(
            self, text="🎯 Target Stock Tracker", 
            font=("Segoe UI", 14, "bold"), fg="#e63946", bg="#1e1e1e"
        )
        self.lbl_title.pack(pady=10)

        # URL Input
        self.lbl_url = tk.Label(self, text="Target Product URL:", fg="#cccccc", bg="#1e1e1e")
        self.lbl_url.pack(anchor="w", padx=20)
        self.entry_url = tk.Entry(self, width=45, bg="#2d2d2d", fg="#ffffff", insertbackground="white")
        self.entry_url.pack(padx=20, pady=2)
        self.entry_url.insert(0, "https://www.target.com/p/needoh-ginger-glowman-fidget-toy/-/A-95271190")

        # Open Link Button
        self.btn_open = tk.Button(
            self, text="🌐 Open Product in Browser", command=self.open_link, 
            bg="#457b9d", fg="#ffffff", font=("Segoe UI", 9, "bold"), width=38
        )
        self.btn_open.pack(pady=6)

        # Status Display Box
        self.lbl_status = tk.Label(
            self, text="Status: Idle", font=("Segoe UI", 11, "bold"), 
            fg="#ffd166", bg="#2d2d2d", width=34, height=2, relief="groove"
        )
        self.lbl_status.pack(pady=6)

        # Action Buttons
        self.btn_frame = tk.Frame(self, bg="#1e1e1e")
        self.btn_frame.pack(pady=5)

        self.btn_check = tk.Button(
            self.btn_frame, text="Check Now", command=self.trigger_check, 
            bg="#06d6a0", fg="#000000", font=("Segoe UI", 9, "bold"), width=12
        )
        self.btn_check.grid(row=0, column=0, padx=5)

        self.btn_auto = tk.Button(
            self.btn_frame, text="Start Auto-Check", command=self.toggle_autocheck, 
            bg="#118ab2", fg="#ffffff", font=("Segoe UI", 9, "bold"), width=15
        )
        self.btn_auto.grid(row=0, column=1, padx=5)

        self.is_monitoring = False

    def open_link(self):
        url = self.entry_url.get().strip()
        if url:
            webbrowser.open(url)
        else:
            messagebox.showerror("Error", "Please enter a valid URL first.")

    def fetch_stock_status(self, target_url):
        payload = {
            'api_key': SCRAPER_API_KEY,
            'url': target_url,
            'render': 'true'
        }
        try:
            response = requests.get('http://api.scraperapi.com', params=payload, timeout=60)
            if response.status_code != 200:
                return f"API Error: HTTP {response.status_code}"

            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()

            if "out of stock" in page_text or "sold out" in page_text:
                return "❌ Out of Stock"
            elif "in stock" in page_text or "add to cart" in page_text or "ship it" in page_text:
                return "✅ IN STOCK!"
            else:
                return "⚠️ Status Uncertain"

        except Exception as e:
            return f"Error: {str(e)[:20]}..."

    def run_check(self):
        url = self.entry_url.get().strip()
        if not url:
            self.update_status("Please enter a valid URL", "#ef476f")
            return

        self.update_status("Fetching status...", "#ffd166")
        status_result = self.fetch_stock_status(url)
        
        color = "#06d6a0" if "IN STOCK" in status_result else ("#ef476f" if "Out" in status_result else "#ffd166")
        self.update_status(status_result, color)

    def trigger_check(self):
        threading.Thread(target=self.run_check, daemon=True).start()

    def update_status(self, text, color):
        self.lbl_status.config(text=f"Status: {text}", fg=color)

    def toggle_autocheck(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.btn_auto.config(text="Stop Auto-Check", bg="#ef476f")
            threading.Thread(target=self.loop_autocheck, daemon=True).start()
        else:
            self.is_monitoring = False
            self.btn_auto.config(text="Start Auto-Check", bg="#118ab2")

    def loop_autocheck(self):
        while self.is_monitoring:
            self.run_check()
            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    app = TargetStockWidget()
    app.mainloop()