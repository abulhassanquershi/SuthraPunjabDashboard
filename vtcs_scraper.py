# #  vtcs_scraper.py
# import sqlite3
# import time

# from datetime import datetime
# now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Configuration
# USERNAME = '3530208541053'
# PASSWORD = 'lgcd1234'
# PORTAL_URL = 'https://suthra.punjab.gov.pk/'
# CHROMEDRIVER_PATH = "E:/chromedriver-win64/chromedriver.exe"
# DB_PATH = "dashboard_data.db"

# # Scrape and store today's VTCS waste collected (in Kg)
# def fetch_vtcs_data():
#     try:
#         # Set up Selenium
#         options = Options()
#         options.add_argument("--start-maximized")
#         options.add_experimental_option("detach", True)  # Browser remains open
#         service = Service(executable_path=CHROMEDRIVER_PATH)
#         driver = webdriver.Chrome(service=service, options=options)

#         # Step 1: Login
#         driver.get(PORTAL_URL)
#         WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="username"]')))
#         driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="username"]').send_keys(USERNAME)
#         driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="password"]').send_keys(PASSWORD)
#         driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
#         WebDriverWait(driver, 20).until(EC.url_contains("/dashboard"))

#         # Step 2: Navigate to VTCS Logs
#         driver.get("https://suthra.punjab.gov.pk/vtcs/view/vtcs-logs")
#         time.sleep(3)

#         # Step 3: Set 100 rows per page and wait for table
#         set_rows_per_page(driver)
#         wait_for_all_rows_to_load(driver)

#         # Step 4: Parse data
#         today_str = datetime.now().strftime('%b %d, %Y')
#         rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
#         total_kg = 0

#         for row in rows:
#             cells = row.find_elements(By.TAG_NAME, 'td')
#             if len(cells) >= 12:
#                 date_time = cells[8].text.strip()
#                 waste = cells[11].text.strip().replace(",", "")
#                 if today_str in date_time:
#                     try:
#                         total_kg += float(waste)
#                     except:
#                         continue

#         result = f"{today_str}: {total_kg:.0f} Kg Collected"
#         print("✅ VTCS Fetched:", result)

#         # Step 5: Save to DB
#         save_to_db(today_str, total_kg)

#         return result

#     except Exception as e:
#         return f"❌ VTCS Error: {e}"

# # Set pagination to 100 rows
# def set_rows_per_page(driver):
#     try:
#         driver.execute_script("window.scrollBy(0, 800);")
#         time.sleep(1)
#         dropdown = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, 'mat-select[aria-label="Items per page:"] .mat-select-trigger'))
#         )
#         dropdown.click()
#         time.sleep(1)
#         option = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, '//mat-option//span[text()="100"]'))
#         )
#         option.click()
#         time.sleep(1)
#     except Exception as e:
#         print(f"⚠️ Pagination setting failed: {e}")

# # Wait until all rows load in table
# def wait_for_all_rows_to_load(driver, timeout=30):
#     end_time = time.time() + timeout
#     previous_count = -1
#     while time.time() < end_time:
#         rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
#         current_count = len(rows)
#         if current_count == previous_count and current_count >= 75:
#             return
#         previous_count = current_count
#         time.sleep(1)
#     raise Exception("⏳ Table did not fully load.")

# # Save collected data to SQLite database
# def save_to_db(date_str, collected_kg):
#     try:
#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS vtcs_data (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 date TEXT UNIQUE,
#                 collected_kg REAL
#             )
#         """)
#         cursor.execute("INSERT OR REPLACE INTO vtcs_data (date, collected_kg) VALUES (?, ?)", (date_str, collected_kg))
#         conn.commit()
#         conn.close()
#         print("✅ VTCS data saved to DB.")
#     except Exception as e:
#         print(f"⚠️ DB Error: {e}")

# # Get today's summary (for dashboard)
# def get_vtcs_summary():
#     try:
#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()
#         today = datetime.now().strftime('%b %d, %Y')
#         cursor.execute("SELECT collected_kg FROM vtcs_data WHERE date=?", (today,))
#         row = cursor.fetchone()
#         conn.close()
#         if row:
#             return f"{today}: {int(row[0]):,} Kg Collected"
#         else:
#             return "No data for today"
#     except Exception as e:
#         return f"❌ DB Error: {e}"

# # Get last 30 entries (for modal detail)
# def get_vtcs_details():
#     try:
#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()
#         cursor.execute("SELECT date, collected_kg FROM vtcs_data ORDER BY date DESC LIMIT 30")
#         rows = cursor.fetchall()
#         conn.close()
#         return [{"Date": row[0], "Collected (Kg)": int(row[1])} for row in rows]
#     except Exception as e:
#         return [{"Error": str(e)}]

# # Run scraper manually for testing
# if __name__ == "__main__":
#     print(fetch_vtcs_data())

import sqlite3
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Config
USERNAME = '3530208541053'
PASSWORD = 'lgcd1234'
PORTAL_URL = 'https://suthra.punjab.gov.pk/'
CHROMEDRIVER_PATH = "E:/chromedriver-win64/chromedriver.exe"
DB_PATH = "dashboard_data.db"

def fetch_vtcs_data():
    print("🚀 Starting VTCS scrape in headless mode...")
    try:
        options = Options()
        options.add_argument("--headless=new")  # ✅ Hide browser (modern headless)
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)

        print("🔐 Logging into portal...")
        driver.get(PORTAL_URL)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="username"]')))
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="username"]').send_keys(USERNAME)
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="password"]').send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'button[type=\"submit\"]').click()
        WebDriverWait(driver, 20).until(EC.url_contains("/dashboard"))

        print("📍 Navigating to VTCS logs...")
        driver.get("https://suthra.punjab.gov.pk/vtcs/view/vtcs-logs")
        time.sleep(3)

        print("📄 Setting rows per page to 100...")
        set_rows_per_page(driver)
        wait_for_all_rows_to_load(driver)

        print("📊 Extracting today’s waste collection data...")
        today_str = datetime.now().strftime('%b %d, %Y')
        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        total_kg = 0

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 12:
                date_time = cells[8].text.strip()
                waste = cells[11].text.strip().replace(",", "")
                if today_str in date_time:
                    try:
                        total_kg += float(waste)
                    except:
                        continue

        result = f"{today_str}: {total_kg:.0f} Kg Collected"
        print("✅ VTCS Collected:", result)

        print("💾 Saving to database...")
        save_to_db(today_str, total_kg)
        print("✅ Done.")

        return result

    except Exception as e:
        return f"❌ VTCS Error: {e}"

def set_rows_per_page(driver):
    try:
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1)
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'mat-select[aria-label="Items per page:"] .mat-select-trigger'))
        )
        dropdown.click()
        time.sleep(1)
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//mat-option//span[text()="100"]'))
        )
        option.click()
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Pagination setting failed: {e}")

def wait_for_all_rows_to_load(driver, timeout=30):
    end_time = time.time() + timeout
    previous_count = -1
    while time.time() < end_time:
        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        current_count = len(rows)
        if current_count == previous_count and current_count >= 75:
            return
        previous_count = current_count
        time.sleep(1)
    raise Exception("⏳ Table did not fully load.")

def save_to_db(date_str, collected_kg):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vtcs_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                collected_kg REAL
            )
        """)
        cursor.execute("INSERT OR REPLACE INTO vtcs_data (date, collected_kg) VALUES (?, ?)", (date_str, collected_kg))
        conn.commit()
        conn.close()
        print("💾 VTCS data saved to DB.")
    except Exception as e:
        print(f"⚠️ DB Error: {e}")

def get_vtcs_summary():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today = datetime.now().strftime('%b %d, %Y')
        cursor.execute("SELECT collected_kg FROM vtcs_data WHERE date=?", (today,))
        row = cursor.fetchone()
        conn.close()
        return f"{today}: {int(row[0]):,} Kg Collected" if row else "No data for today"
    except Exception as e:
        return f"❌ DB Error: {e}"

def get_vtcs_details():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT date, collected_kg FROM vtcs_data ORDER BY date DESC LIMIT 30")
        rows = cursor.fetchall()
        conn.close()
        return [{"Date": row[0], "Collected (Kg)": int(row[1])} for row in rows]
    except Exception as e:
        return [{"Error": str(e)}]

if __name__ == "__main__":
    print(fetch_vtcs_data())
