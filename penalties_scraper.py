from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import defaultdict
import sqlite3
import json
from datetime import datetime
import time

# Config
USERNAME = '3530208541053'
PASSWORD = 'lgcd1234'
PORTAL_URL = 'https://suthra.punjab.gov.pk/'
PENALTY_URL = 'https://suthra.punjab.gov.pk/penalty-management/view/contractor-penalties'
CHROMEDRIVER_PATH = "E:/chromedriver-win64/chromedriver.exe"

def fetch_penalty_summary():
    print("🚀 Launching headless browser...")
    options = Options()
    options.add_argument("--headless=new")  # ✅ Headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("🔐 Logging in to Suthra Punjab...")
        driver.get(PORTAL_URL)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="username"]'))
        )
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="username"]').send_keys(USERNAME)
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="password"]').send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(5)

        print("📍 Navigating to Penalty Management...")
        driver.get(PENALTY_URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        time.sleep(3)

        # Set pagination to 100
        try:
            dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'mat-select[aria-label="Items per page:"] .mat-select-trigger'))
            )
            dropdown.click()
            time.sleep(1)
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//mat-option//span[text()="100"]'))
            )
            option.click()
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Pagination error: {e}")

        print("🔍 Scanning penalty rows...")
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(1)

        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        today_str = datetime.now().strftime('%b %d, %Y')

        total_amount = 0
        total_penalties = 0
        penalty_counts = defaultdict(int)
        penalty_details = []

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 10:
                imposed = cells[9].text.strip()
                date_str = cells[7].text.strip()
                sub_type = cells[5].text.strip()
                amount_str = cells[6].text.strip().replace(",", "")

                if today_str in date_str:
                    try:
                        amount = float(amount_str)
                    except:
                        amount = 0.0
                    total_amount += amount
                    total_penalties += 1
                    penalty_counts[sub_type] += 1

                    penalty_details.append({
                        'type': sub_type,
                        'amount': amount,
                        'date': date_str,
                        'imposed': imposed != '-'
                    })

        print(f"✅ Penalties for {today_str}: {total_penalties} total, Rs. {total_amount}")
        print("📌 Breakdown by Type:", dict(penalty_counts))
        print("💾 Saving to database...")

        save_to_db(today_str, total_penalties, total_amount, penalty_counts, penalty_details)

    except Exception as e:
        print(f"❌ Penalties fetch error: {e}")
    finally:
        driver.quit()
        print("🧹 Browser closed.")

def save_to_db(date_str, total, amount, breakdown, details):
    try:
        conn = sqlite3.connect("dashboard_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS penalties_data (
                date TEXT PRIMARY KEY,
                total_penalties INTEGER,
                total_amount REAL,
                breakdown TEXT,
                details_json TEXT
            )
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO penalties_data 
            (date, total_penalties, total_amount, breakdown, details_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            date_str,
            total,
            amount,
            json.dumps(dict(breakdown)),
            json.dumps(details)
        ))
        conn.commit()
        conn.close()
        print("✅ Penalty data saved to DB including details_json.")
    except Exception as e:
        print(f"⚠️ DB insert error: {e}")

# Run directly
if __name__ == "__main__":
    fetch_penalty_summary()
