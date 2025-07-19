from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import defaultdict
import sqlite3
import time

PORTAL_URL = 'https://suthra.punjab.gov.pk/'
USERNAME = '3530208541053'
PASSWORD = 'lgcd1234'
CHROMEDRIVER_PATH = "E:/chromedriver-win64/chromedriver.exe"

IGNORED_DESIGNATIONS = {
    "Assistant Tehsil Manager Operations",
    "Data Entery Operator",
    "Manager HR and Admin",
    "Monitoring Officer",
    "Security Guard",
    "Transport Incharge"
}

def fetch_attendance_summary():
    print("🚀 Starting Attendance scraper...")
    options = Options()
    options.add_argument("--headless=new")  # ✅ Hidden browser
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("🔐 Logging in...")
        driver.get(PORTAL_URL)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="username"]'))
        )
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="username"]').send_keys(USERNAME)
        driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="password"]').send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'button[type=\"submit\"]').click()
        time.sleep(5)

        print("📍 Navigating to attendance report...")
        driver.get('https://suthra.punjab.gov.pk/solid-waste/attendance/worker-last-seven-day')
        time.sleep(5)

        print("📄 Selecting dropdown filters...")
        for i in range(3):
            selects = driver.find_elements(By.TAG_NAME, 'mat-select')
            if i < len(selects):
                selects[i].click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'mat-option'))
                )
                options_list = driver.find_elements(By.TAG_NAME, 'mat-option')
                for option in options_list:
                    if option.get_attribute("aria-disabled") == "false":
                        option.click()
                        break
                time.sleep(1)

        print("🔍 Clicking Search...")
        driver.find_element(By.XPATH, '//button[contains(text(),"Search")]').click()
        WebDriverWait(driver, 60).until(lambda d: "Sr#" in d.find_element(By.CSS_SELECTOR, "table").text)

        print("📥 Loading rows...")
        last_row_count = 0
        for _ in range(100):
            driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(0.4)
            rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
            if len(rows) == last_row_count:
                break
            last_row_count = len(rows)

        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        if not rows:
            raise Exception("No rows found in attendance table.")

        headers = rows[0].find_elements(By.TAG_NAME, 'td')
        last_col_index = len(headers) - 1
        date_str = headers[last_col_index].text.strip()

        present = halfday = holiday = absent = total = 0
        absent_list = []
        assign_type_counter = defaultdict(int)

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) <= last_col_index:
                continue

            status = cells[last_col_index].text.strip().upper()
            name = cells[1].text.strip()
            designation = cells[3].text.strip()
            assign_type = cells[6].text.strip()
            uc = cells[10].text.strip()

            if not assign_type or assign_type.lower() == "null" or designation in IGNORED_DESIGNATIONS:
                continue

            assign_type_counter[assign_type] += 1

            if status in ["P", "P2"]:
                present += 1
            elif status == "P1":
                halfday += 1
            elif status == "H":
                holiday += 1
            elif status == "A":
                absent += 1
                absent_list.append((name, designation, uc))

            total += 1

        summary_text = (
            f"📅 Date: {date_str} | "
            f"✅ Present: {present} | "
            f"½ Day: {halfday} | "
            f"🏖️ Holiday: {holiday} | "
            f"❌ Absent: {absent}"
        )

        detail_lines = ["<h5 class='mb-3'>🧭 By Assign Type (all assigned workers):</h5>"]
        detail_lines.append("<table class='table table-bordered'><thead><tr><th>Assign Type</th><th>Count</th></tr></thead><tbody>")
        for assign, count in sorted(assign_type_counter.items()):
            detail_lines.append(f"<tr><td>{assign}</td><td>{count}</td></tr>")
        detail_lines.append("</tbody></table>")

        grouped = defaultdict(list)
        for name, desig, uc in absent_list:
            grouped[uc].append((name, desig))

        detail_lines.append("<h5 class='mt-4'>🧍‍♂️ Absent Workers:</h5>")
        detail_lines.append("<table class='table table-bordered'><thead><tr><th>Sr#</th><th>Name</th><th>Designation</th><th>UC</th></tr></thead><tbody>")
        sr = 1
        for uc, entries in sorted(grouped.items()):
            for name, desig in entries:
                detail_lines.append(f"<tr><td>{sr}</td><td>{name}</td><td>{desig}</td><td>{uc}</td></tr>")
                sr += 1
        detail_lines.append("</tbody></table>")

        detail_html = "\n".join(detail_lines)

        save_to_db(date_str, summary_text, detail_html)
        print("✅ Attendance fetched and saved successfully.")

        return summary_text, detail_html

    except Exception as e:
        print(f"❌ Attendance Error: {e}")
        return "Attendance Error", "<p>Error fetching data.</p>"

    finally:
        driver.quit()

def save_to_db(date_str, summary, detail):
    try:
        conn = sqlite3.connect("dashboard_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attendance_data (date, summary, absent_detail)
            VALUES (?, ?, ?)
        """, (date_str, summary, detail))
        conn.commit()
        conn.close()
        print("💾 Attendance data saved to DB.")
    except Exception as e:
        print(f"⚠️ DB Save Error: {e}")

if __name__ == "__main__":
    fetch_attendance_summary()
