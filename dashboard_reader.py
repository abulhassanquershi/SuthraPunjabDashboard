# dashboard_reader.py
import sqlite3

def get_latest_vtcs():
    conn = sqlite3.connect("dashboard_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, collected_kg FROM vtcs_data ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return f"🗑️ {result[0]}: {result[1]} KG collected" if result else "VTCS: No data"

def get_latest_vtms():
    conn = sqlite3.connect("dashboard_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, active, inactive FROM vtms_data ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return f"🚛 {result[0]} - Active: {result[1]} | Inactive: {result[2]}" if result else "VTMS: No data"

def get_latest_attendance():
    conn = sqlite3.connect("dashboard_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, summary FROM attendance_data ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[1] if result else "Attendance: No data"

def get_latest_ped():
    conn = sqlite3.connect("dashboard_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, summary FROM ped_data ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[1] if result else "PED: No data"

def get_latest_container():
    conn = sqlite3.connect("dashboard_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, count FROM container_data ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return f"🗑️ {result[0]}: {result[1]} container services" if result else "Containers: No data"

def get_latest_penalties():
    conn = sqlite3.connect("dashboard_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, total_penalties, total_amount FROM penalties_data ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return f"⚠️ {result[0]}: {result[1]} penalties | Rs. {result[2]:,.0f}" if result else "Penalties: No data"
