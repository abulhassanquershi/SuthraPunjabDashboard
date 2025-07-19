import sqlite3
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

class PEDScraper:
    def __init__(self):
        self.USERNAME = '3530208541053'
        self.PASSWORD = 'lgcd1234'
        self.PORTAL_URL = 'https://suthra.punjab.gov.pk/'
        self.PED_URL = 'https://suthra.punjab.gov.pk/ped/ped-tehsil-report'
        self.CHROMEDRIVER_PATH = "E:/chromedriver-win64/chromedriver.exe"
        self.driver = None

    def setup_browser(self):
        print("🚀 Starting browser in headless mode...")
        options = Options()
        options.add_argument("--headless")  # Hide browser
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        service = Service(self.CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=options)

    def login(self):
        print("🔐 Logging in to portal...")
        self.driver.get(self.PORTAL_URL)
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="username"]')))
        self.driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="username"]').send_keys(self.USERNAME)
        self.driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="password"]').send_keys(self.PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(5)

    def navigate_to_ped(self):
        print("📍 Navigating to PED Tehsil Report page...")
        self.driver.get(self.PED_URL)
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'mat-select')))
        time.sleep(2)

        for i in range(3):
            selects = self.driver.find_elements(By.TAG_NAME, 'mat-select')
            if i < len(selects):
                selects[i].click()
                time.sleep(1)
                options_list = self.driver.find_elements(By.CLASS_NAME, 'mat-option')
                if options_list:
                    options_list[0].click()
                time.sleep(1)

        print("🔍 Clicking Search...")
        search_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Search")]'))
        )
        search_btn.click()
        time.sleep(5)

    def extract_data(self):
        print("📊 Extracting data from table...")
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        poor_performance = []
        total_score = 0.0
        obtained_score = 0.0

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 10:
                try:
                    activity = cells[1].text.strip()
                    key_factor = cells[3].text.strip()
                    total = float(cells[7].text.strip()) if cells[7].text.strip() else 0.0
                    obtained = float(cells[8].text.strip()) if cells[8].text.strip() else 0.0
                    invoice = cells[9].text.strip()

                    total_score += total
                    obtained_score += obtained

                    if obtained < total:
                        poor_performance.append({
                            "Activity": activity,
                            "Key Factor": key_factor,
                            "Score": f"{obtained:.1f}/{total:.1f}",
                            "Invoice": invoice
                        })
                except Exception:
                    continue

        summary_json = json.dumps(poor_performance)
        self.save_to_db(obtained_score, total_score, summary_json)

        return f"✅ Total Score: {obtained_score:.2f}/{total_score:.2f} (Saved)"

    def save_to_db(self, obtained, total, summary_json):
        try:
            conn = sqlite3.connect("dashboard_data.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ped_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    obtained_score REAL,
                    total_score REAL,
                    summary TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO ped_data (date, obtained_score, total_score, summary)
                VALUES (?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d"),
                round(obtained, 2),
                round(total, 2),
                summary_json
            ))
            conn.commit()
            conn.close()
            print("💾 PED data saved to database.")
        except Exception as e:
            print(f"⚠️ DB insert error: {e}")

    def run(self):
        try:
            self.setup_browser()
            self.login()
            self.navigate_to_ped()
            result = self.extract_data()
            print(result)
            return result
        except Exception as e:
            print(f"❌ PED Error: {e}")
            return f"❌ PED Error: {e}"
        finally:
            self.driver.quit()

# Run standalone
if __name__ == "__main__":
    scraper = PEDScraper()
    scraper.run()
