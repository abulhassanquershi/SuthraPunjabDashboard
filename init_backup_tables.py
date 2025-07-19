import sqlite3

conn = sqlite3.connect("dashboard_data.db")
cursor = conn.cursor()

tables = [
    "vtcs_data", "vtms_data", "ped_data", "attendance_data",
    "container_data", "penalties_data"
]

for table in tables:
    backup_table = f"backup_{table}"
    try:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {backup_table} AS SELECT * FROM {table} WHERE 0")
        print(f"✅ Created {backup_table}")
    except Exception as e:
        print(f"❌ Failed to create {backup_table}: {e}")

conn.commit()
conn.close()
print("🎉 All backup tables initialized.")
