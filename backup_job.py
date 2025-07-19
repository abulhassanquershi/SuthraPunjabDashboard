import sqlite3
from datetime import datetime
import shutil

DB = "dashboard_data.db"
BACKUP_DB = "dashboard_data_backup.db"

def backup_table(conn, source, target):
    cursor = conn.cursor()
    # Clear old backup
    cursor.execute(f"DELETE FROM {target}")
    # Copy all rows from source to backup
    cursor.execute(f"INSERT INTO {target} SELECT * FROM {source}")
    print(f"✅ Backed up {source} → {target}")
    conn.commit()

def run_backup():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"📦 Running final backup at {now}...")

    conn = sqlite3.connect(DB)
    backup_table(conn, "vtcs_data", "backup_vtcs_data")
    backup_table(conn, "vtms_data", "backup_vtms_data")
    backup_table(conn, "ped_data", "backup_ped_data")
    backup_table(conn, "attendance_data", "backup_attendance_data")
    backup_table(conn, "container_data", "backup_container_data")
    backup_table(conn, "penalties_data", "backup_penalties_data")
    conn.close()
    print("🎉 Final backup complete.")

run_backup()
