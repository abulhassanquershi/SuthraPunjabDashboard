import schedule
import time
import os
from datetime import datetime

def run_scrapers():
    now = datetime.now()
    hour = now.hour
    if 6 <= hour <= 18:  # Run only during 6AM–6PM
        print(f"🕒 {now.strftime('%H:%M')} Running scrapers...")
        os.system("python vtcs_scraper.py")
        os.system("python vtms_scraper.py")
        os.system("python ped_scraper.py")
        os.system("python attendance_scraper.py")
        os.system("python container_scraper.py")
        os.system("python penalties_scraper.py")
    else:
        print("❌ Outside working hours. Skipping scrapers.")

# Schedule scrapers every 2 hours
schedule.every(2).hours.do(run_scrapers)

# Run once on startup
run_scrapers()

print("✅ Scheduler started. Running every 2 hours (6AM–6PM)...")
while True:
    schedule.run_pending()
    time.sleep(60)
