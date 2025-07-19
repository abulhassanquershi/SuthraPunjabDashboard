import sqlite3

conn = sqlite3.connect("dashboard_data.db")
cursor = conn.cursor()

# Create VTCS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS vtcs_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    collected_kg REAL,
    summary TEXT
)
""")

# Create VTMS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS vtms_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    active_count INTEGER,
    inactive_count INTEGER,
    vehicle_detail TEXT
)
""")

# Create Attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    summary TEXT,
    absent_detail TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully.")
