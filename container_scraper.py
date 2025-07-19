
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from collections import defaultdict
import time

# Config
USERNAME = '3530208541053'
PASSWORD = 'lgcd1234'
PORTAL_URL = 'https://suthra.punjab.gov.pk/'
TARGET_URL = 'https://suthra.punjab.gov.pk/solid-waste/sw-logs/view/sw-service-logs'
CHROMEDRIVER_PATH = "E:/chromedriver-win64/chromedriver.exe"

def fetch_container_summary():
    print("🚀 Starting container data extraction...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("detach", False)

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("🔐 Logging in...")
        driver.get(PORTAL_URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="username"]')))
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="username"]').send_keys(USERNAME)
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="password"]').send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(5)

        print("🌐 Navigating to container service log...")
        driver.get(TARGET_URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        time.sleep(2)

        # Set rows per page to 100
        try:
            print("🔢 Setting rows per page to 100...")
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
            print(f"⚠️ Rows-per-page error: {e}")

        print("📄 Loading and parsing rows...")
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(1)

        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        target_date = datetime.now().strftime("%b %d, %Y")

        matched_rows = 0
        urban_count = 0
        rural_count = 0
        vehicle_data = defaultdict(lambda: {'count': 0, 'time_count': 0})

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 16:
                submitted_date = cells[15].text.strip()
                if target_date in submitted_date:
                    matched_rows += 1
                    area = cells[3].text.strip().lower()
                    vehicle_name = cells[6].text.strip()
                    try:
                        time_count = int(cells[2].text.strip())
                    except:
                        time_count = 1  # fallback

                    if area == "urban":
                        urban_count += 1
                    elif area == "rural":
                        rural_count += 1

                    vehicle_data[vehicle_name]['count'] += 1
                    vehicle_data[vehicle_name]['time_count'] += time_count

        print(f"📦 Total: {matched_rows} | 🌆 Urban: {urban_count} | 🌄 Rural: {rural_count}")
        print("🛻 Vehicle Summary:")
        for idx, (veh, stats) in enumerate(vehicle_data.items(), 1):
            print(f"{idx}. {veh} | Count: {stats['count']} | Time Count: {stats['time_count']}")

        save_to_db(target_date, matched_rows, urban_count, rural_count, vehicle_data)

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        driver.quit()
        print("✅ Container scraping completed.")

def save_to_db(date_str, total_entries, urban_entries, rural_entries, vehicle_dict):
    try:
        conn = sqlite3.connect("dashboard_data.db")
        cursor = conn.cursor()

        # Drop and recreate detail table (to fix column issues)
        cursor.execute("DROP TABLE IF EXISTS container_detail")
        cursor.execute("""
            CREATE TABLE container_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                vehicle TEXT,
                collected INTEGER,
                time_count INTEGER
            )
        """)

        # Create summary table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS container_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                count INTEGER,
                urban INTEGER,
                rural INTEGER
            )
        """)

        # Insert summary
        cursor.execute("INSERT INTO container_data (date, count, urban, rural) VALUES (?, ?, ?, ?)",
                       (date_str, total_entries, urban_entries, rural_entries))

        # Insert detail rows
        for vehicle, data in vehicle_dict.items():
            cursor.execute("""
                INSERT INTO container_detail (date, vehicle, collected, time_count)
                VALUES (?, ?, ?, ?)
            """, (date_str, vehicle, data['count'], data['time_count']))

        conn.commit()
        conn.close()
        print("💾 Data saved successfully to database.")

    except Exception as e:
        print(f"⚠️ DB Save Error: {e}")

# Run
if __name__ == "__main__":
    fetch_container_summary()
