#  vtms_scraper.py
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

USERNAME = '3530208541053'
PASSWORD = 'lgcd1234'
PORTAL_URL = 'https://suthra.punjab.gov.pk/'
VTMS_URL = 'https://suthra.punjab.gov.pk/vtms/view/vtms-logs'
CHROMEDRIVER_PATH = "E:/chromedriver-win64/chromedriver.exe"
DB_PATH = "dashboard_data.db"


def fetch_vtms_data():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Login
        driver.get(PORTAL_URL)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="username"]')))
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="username"]').send_keys(USERNAME)
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="password"]').send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(5)

        # Go to VTMS page
        driver.get(VTMS_URL)
        time.sleep(5)

        set_rows_per_page(driver)
        wait_for_all_rows_to_load(driver)

        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        today = datetime.now().strftime('%Y-%m-%d')
        active = 0
        inactive = 0
        seen_vehicles = set()
        inactive_details = []

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 19:
                status = cells[18].text.strip().lower()
                vehicle = cells[4].text.strip()
                vehicle_type = cells[16].text.strip()
                distance = cells[6].text.strip()
                work_minutes = cells[7].text.strip()
                work_hours = cells[8].text.strip()

                if not vehicle:
                    continue

                key = (vehicle, status)
                if key in seen_vehicles:
                    continue
                seen_vehicles.add(key)

                if status == "inactive":
                    inactive += 1
                    inactive_details.append({
                        "vehicle": vehicle,
                        "vehicle_type": vehicle_type,
                        "distance": distance,
                        "work_hours": work_hours,
                        "work_minutes": work_minutes,
                        "status": "Inactive"
                    })
                elif status == "active":
                    active += 1

        summary = f"🟢 Active: {active} | 🔴 Inactive: {inactive}"
        save_to_db(today, active, inactive, summary, inactive_details)
        print("✅ VTMS data updated from portal.")
        print(summary)
        return summary

    except Exception as e:
        return f"❌ VTMS Error: {str(e)}"

    finally:
        driver.quit()


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
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Pagination error: {e}")


def wait_for_all_rows_to_load(driver, timeout=30):
    end_time = time.time() + timeout
    last_count = -1
    while time.time() < end_time:
        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        if len(rows) == last_count and len(rows) >= 75:
            return
        last_count = len(rows)
        time.sleep(1)
    raise Exception("⏳ VTMS data load timeout.")


def save_to_db(date, active_count, inactive_count, summary, inactive_list):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vtms_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                active_count INTEGER,
                inactive_count INTEGER,
                summary TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vtms_inactive_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                vehicle TEXT,
                vehicle_type TEXT,
                distance TEXT,
                work_hours TEXT,
                work_minutes TEXT,
                status TEXT
            )
        """)

        # Delete today's old data
        cursor.execute("DELETE FROM vtms_data WHERE date = ?", (date,))
        cursor.execute("DELETE FROM vtms_inactive_details WHERE date = ?", (date,))

        for item in inactive_list:
            cursor.execute("""
                INSERT INTO vtms_inactive_details (date, vehicle, vehicle_type, distance, work_hours, work_minutes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                item['vehicle'],
                item['vehicle_type'],
                item['distance'],
                item['work_hours'],
                item['work_minutes'],
                item['status']
            ))

        cursor.execute("INSERT INTO vtms_data (date, active_count, inactive_count, summary) VALUES (?, ?, ?, ?)",
                       (date, active_count, inactive_count, summary))

        conn.commit()
        conn.close()
        print("✅ VTMS data + inactive details saved to DB.")
    except Exception as e:
        print(f"⚠️ DB error: {e}")


def get_vtms_summary():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT summary FROM vtms_data WHERE date=? ORDER BY id DESC LIMIT 1", (today,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else "No data"
    except Exception as e:
        return f"❌ {e}"


def get_vtms_details():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT vehicle, vehicle_type, distance, work_hours, work_minutes, status
            FROM vtms_inactive_details
            WHERE date=?
            ORDER BY vehicle_type ASC
        """, (today,))
        rows = cursor.fetchall()
        conn.close()
        return [{
            "Vehicle": row[0],
            "Vehicle Type": row[1],
            "Distance": row[2],
            "Work Hours": row[3],
            "Work Minutes": row[4],
            "Status": row[5]
        } for row in rows]
    except Exception as e:
        return [{"Error": str(e)}]


if __name__ == "__main__":
    print(fetch_vtms_data())
