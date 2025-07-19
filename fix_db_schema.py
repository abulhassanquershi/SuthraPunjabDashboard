# import sqlite3

# def check_attendance_data():
#     try:
#         conn = sqlite3.connect("dashboard_data.db")
#         cursor = conn.cursor()
#         cursor.execute("SELECT id, date, summary FROM attendance_data ORDER BY id DESC LIMIT 5")
#         rows = cursor.fetchall()

#         if not rows:
#             print("❌ No attendance records found in the database.")
#         else:
#             print("✅ Last 5 Attendance Records:")
#             for row in rows:
#                 print(f"\nID: {row[0]}\nDate: {row[1]}\nSummary:\n{row[2]}")
        
#         conn.close()

#     except Exception as e:
#         print(f"⚠️ Error reading DB: {e}")

# # Run it
# check_attendance_data()
# import sqlite3

# conn = sqlite3.connect("suthra_dashboard.db")
# cursor = conn.cursor()

# # Create the table if it doesn't exist
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS vtms_data (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     date TEXT,
#     active_count INTEGER,
#     inactive_count INTEGER,
#     vehicle_detail TEXT  -- This stores the JSON array of vehicle info
# )
# """)

# conn.commit()
# conn.close()

# print("✅ vtms_data table ensured with vehicle_detail column.")
##########################

#########**************############



# import sqlite3, json
# from datetime import datetime

# # Let's say you have a list like this after scraping
# vehicle_data = [
#     {"Vehicle #": "FSD-123", "Status": "Active", "Type": "Dumper"},
#     {"Vehicle #": "FSD-456", "Status": "Inactive", "Type": "Loader"},
#     # ... more vehicles
# ]

# # Count totals
# active_count = sum(1 for v in vehicle_data if v["Status"].lower() == "active")
# inactive_count = sum(1 for v in vehicle_data if v["Status"].lower() == "inactive")
# today_str = datetime.today().strftime("%Y-%m-%d")

# # Insert into vtms_data table
# conn = sqlite3.connect("suthra_dashboard.db")
# cursor = conn.cursor()
# cursor.execute("""
#     INSERT INTO vtms_data (date, active_count, inactive_count, vehicle_detail)
#     VALUES (?, ?, ?, ?)
# """, (today_str, active_count, inactive_count, json.dumps(vehicle_data)))
# # conn.commit()
# # conn.close()

# print("✅ VTMS data inserted into database.")









# import sqlite3

# conn = sqlite3.connect("dashboard_data.db")
# cursor = conn.cursor()

# # Check if column exists
# cursor.execute("PRAGMA table_info(vtms_data)")
# columns = [col[1] for col in cursor.fetchall()]

# if "vehicle_detail" not in columns:
#     cursor.execute("ALTER TABLE vtms_data ADD COLUMN vehicle_detail TEXT")
#     print("✅ Column 'vehicle_detail' added to vtms_data.")
# else:
#     print("✅ Column already exists.")

# conn.commit()
# conn.close()




# import sqlite3
# import json

# # Example summary & vehicle list
# summary = "2025-07-14 — 🟢 71 | 🔴 9"
# vehicle_data_list = [
#     {"Vehicle No": "FSD-001", "Status": "Active", "Type": "Loader"},
#     {"Vehicle No": "FSD-002", "Status": "Inactive", "Type": "Tipper"},
#     # etc...
# ]

# # Convert to JSON
# vehicle_json = json.dumps(vehicle_data_list)

# # Store in DB
# conn = sqlite3.connect("dashboard_data.db")
# cursor = conn.cursor()

# cursor.execute("""
#     INSERT INTO vtms_data (summary, vehicle_detail)
#     VALUES (?, ?)
# """, (summary, vehicle_json))

# conn.commit()
# conn.close()
# print("✅ VTMS data saved with vehicle details.")


# import sqlite3

# conn = sqlite3.connect("dashboard_data.db")
# cursor = conn.cursor()
# cursor.execute("ALTER TABLE vtcs_data ADD COLUMN summary TEXT")
# conn.commit()
# conn.close()
# print("✅ Added summary column to vtcs_data.")


# import sqlite3

# conn = sqlite3.connect("dashboard_data.db")
# cursor = conn.cursor()
# cursor.execute("PRAGMA table_info(vtcs_data)")
# columns = cursor.fetchall()

# for col in columns:
#     print(col)
# conn.close()


# import sqlite3
# conn = sqlite3.connect("dashboard_data.db")
# cursor = conn.cursor()
# cursor.execute("PRAGMA table_info(vtms_data)")
# print(cursor.fetchall())



##########################( VTMS )

# import sqlite3

# conn = sqlite3.connect("dashboard_data.db")
# cursor = conn.cursor()

# # Drop the old table (if it exists)
# cursor.execute("DROP TABLE IF EXISTS vtms_inactive_details")
# conn.commit()
# conn.close()

# print("✅ Old vtms_inactive_details table dropped.")

# import sqlite3

# conn = sqlite3.connect("dashboard_data.db")
# cursor = conn.cursor()

# # ❌ Drop the old incorrect table
# cursor.execute("DROP TABLE IF EXISTS vtms_inactive_details")

# conn.commit()
# conn.close()

# print("✅ Old 'vtms_inactive_details' table dropped successfully.")



#########################################
            ##******  PED START TESTING *******####
##############################################

# import sqlite3

# DB_PATH = "dashboard_data.db"

# def check_ped_data():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     try:
#         cursor.execute("SELECT id, date, obtained_score, total_score, summary FROM ped_data ORDER BY id DESC")
#         rows = cursor.fetchall()
#         if not rows:
#             print("❌ No PED data found.")
#         else:
#             for row in rows:
#                 print(f"\n🧾 ID: {row[0]}")
#                 print(f"📅 Date: {row[1]}")
#                 print(f"✅ Obtained Score: {row[2]} / {row[3]}")
#                 print("📋 Summary:")
#                 print(row[4])
#                 print("-" * 50)
#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         conn.close()

# if __name__ == "__main__":
#     check_ped_data()

#####################################################

#########################################
            ##******  Attendecne check in database*******####
##############################################
# import sqlite3

# def show_latest_attendance():
#     conn = sqlite3.connect("dashboard_data.db")
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT date, summary FROM attendance_data
#         ORDER BY id DESC LIMIT 1
#     """)
#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         print(f"📅 Date: {result[0]}")
#         print(result[1])
#     else:
#         print("No attendance data found.")

# show_latest_attendance()




#########################################
            ##******  Container services *******####
##############################################

# import sqlite3

# conn = sqlite3.connect('dashboard_data.db')
# cursor = conn.cursor()

# try:
#     cursor.execute("ALTER TABLE container_data ADD COLUMN urban INTEGER DEFAULT 0")
# except sqlite3.OperationalError:
#     print("Column 'urban' already exists.")

# try:
#     cursor.execute("ALTER TABLE container_data ADD COLUMN rural INTEGER DEFAULT 0")
# except sqlite3.OperationalError:
#     print("Column 'rural' already exists.")

# conn.commit()
# conn.close()
# print("Database schema updated (if needed).")





#########################################
            ##******  Panlitess *******####
##############################################
# import sqlite3
# import json

# DB_PATH = 'dashboard_data.db'

# def ensure_penalties_schema(cursor):
#     # Create table if not exists
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS penalties_data (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT,
#             total_amount REAL
#         )
#     """)

#     # Add missing columns
#     try:
#         cursor.execute("ALTER TABLE penalties_data ADD COLUMN count INTEGER DEFAULT 0")
#     except sqlite3.OperationalError:
#         pass  # Already exists

#     try:
#         cursor.execute("ALTER TABLE penalties_data ADD COLUMN detail_json TEXT")
#     except sqlite3.OperationalError:
#         pass  # Already exists

# def show_latest_penalty_record(cursor):
#     try:
#         cursor.execute("SELECT date, total_amount, count, detail_json FROM penalties_data ORDER BY id DESC LIMIT 1")
#         row = cursor.fetchone()

#         if row:
#             date, total_amount, count, detail_json = row
#             print("✅ Latest Penalty Record:")
#             print(f"📅 Date: {date}")
#             print(f"💰 Total Amount: Rs. {total_amount}")
#             print(f"📋 Entries Count: {count}")
#             print("📄 Penalty Details:")
#             try:
#                 details = json.loads(detail_json)
#                 for i, entry in enumerate(details, 1):
#                     penalty_type = entry.get("Penalty Type", "N/A")
#                     amount = entry.get("Penalty Amount", "N/A")
#                     status = entry.get("Status", "N/A")
#                     print(f"  {i}. {penalty_type} - Rs. {amount} ({status})")
#             except Exception as e:
#                 print(f"⚠️ Error parsing JSON: {e}")
#         else:
#             print("ℹ️ No records found in penalties_data.")

#     except Exception as e:
#         print(f"❌ Error reading penalties_data: {e}")

# # Run the check
# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()

# ensure_penalties_schema(cursor)
# show_latest_penalty_record(cursor)

# conn.commit()
# conn.close()

# import sqlite3

# conn = sqlite3.connect('dashboard_data.db')
# cursor = conn.cursor()

# try:
#     cursor.execute("ALTER TABLE penalties_data ADD COLUMN details_json TEXT")
#     print("✅ Column 'details_json' added.")
# except sqlite3.OperationalError as e:
#     if "duplicate column name" in str(e).lower():
#         print("ℹ️ Column 'details_json' already exists.")
#     else:
#         print(f"⚠️ Error: {e}")

# conn.commit()
# conn.close()


####################################################schelue 

# import schedule
# import time

# def job():
#     print("✅ Scheduled job ran!")

# schedule.every(1).minutes.do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)


######################
# import sqlite3

# conn = sqlite3.connect("dashboard_data.db")
# cursor = conn.cursor()

# tables = [
#     "vtcs_data", "vtms_data", "ped_data",
#     "attendance_data", "container_data", "penalties_data"
# ]

# for table in tables:
#     cursor.execute(f"DROP TABLE IF EXISTS backup_{table}")
#     cursor.execute(f"CREATE TABLE backup_{table} AS SELECT * FROM {table} WHERE 0")
#     print(f"✅ Created backup_{table}")

# conn.commit()
# conn.close()


# import sqlite3

# DB_PATH = "dashboard_data.db"

# tables = [
#     "vtcs_data",
#     "vtms_data",
#     "ped_data",
#     "attendance_data",
#     "container_data",
#     "penalties_data"
# ]

# def add_updated_at_column():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     for table in tables:
#         try:
#             # Check if column already exists
#             cursor.execute(f"PRAGMA table_info({table})")
#             columns = [col[1] for col in cursor.fetchall()]
#             if "updated_at" not in columns:
#                 print(f"Adding 'updated_at' column to {table}...")
#                 cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_at TEXT")
#             else:
#                 print(f"'updated_at' already exists in {table}")
#         except Exception as e:
#             print(f"Error updating {table}: {e}")

#     conn.commit()
#     conn.close()
#     print("✅ All tables checked and updated.")

# if __name__ == "__main__":
#     add_updated_at_column()


# update_penalty_table.py


# import sqlite3
# from datetime import datetime

# def update_penalty_database_schema():
#     conn = sqlite3.connect("suthra_dashboard.db")
#     cursor = conn.cursor()

#     # 1. Create penalties summary table (if not exists)
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS penalties_data (
#             date TEXT PRIMARY KEY,
#             total_penalties INTEGER,
#             total_amount REAL,
#             breakdown TEXT
#         )
#     """)

#     # 2. Create penalties detail table (new)
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS penalty_records (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             date TEXT,
#             penalty_id TEXT,
#             district TEXT,
#             office TEXT,
#             penalty_type TEXT,
#             sub_type TEXT,
#             amount REAL,
#             status TEXT,
#             imposed TEXT,
#             contractor TEXT,
#             added_by TEXT,
#             latlong TEXT,
#             created_datetime TEXT
#         )
#     """)

#     conn.commit()
#     conn.close()
#     print("✅ Penalty database schema updated.")

# def insert_penalty_records(records, total_summary):
#     """
#     `records` should be a list of dictionaries with keys:
#     date, penalty_id, district, office, penalty_type, sub_type, amount,
#     status, imposed, contractor, added_by, latlong, created_datetime

#     `total_summary` is a dictionary: {
#         "date": ..., "total_penalties": ..., "total_amount": ..., "breakdown": ...
#     }
#     """
#     conn = sqlite3.connect("suthra_dashboard.db")
#     cursor = conn.cursor()

#     today = total_summary['date']

#     # Clear today's existing data
#     cursor.execute("DELETE FROM penalty_records WHERE date = ?", (today,))
#     cursor.execute("DELETE FROM penalties_data WHERE date = ?", (today,))

#     # Insert summary
#     cursor.execute("""
#         INSERT INTO penalties_data (date, total_penalties, total_amount, breakdown)
#         VALUES (?, ?, ?, ?)
#     """, (
#         today,
#         total_summary['total_penalties'],
#         total_summary['total_amount'],
#         total_summary['breakdown']
#     ))

#     # Insert each detailed record
#     for row in records:
#         cursor.execute("""
#             INSERT INTO penalty_records (
#                 date, penalty_id, district, office, penalty_type,
#                 sub_type, amount, status, imposed, contractor,
#                 added_by, latlong, created_datetime
#             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """, (
#             row['date'], row['penalty_id'], row['district'], row['office'], row['penalty_type'],
#             row['sub_type'], row['amount'], row['status'], row['imposed'], row['contractor'],
#             row['added_by'], row['latlong'], row['created_datetime']
#         ))

#     conn.commit()
#     conn.close()
#     print("📋 Penalty Details:\n✅ Penalty data saved to DB.")

# # Example usage
# if __name__ == "__main__":
#     update_penalty_database_schema()

#     # Test insert (you can remove this block when integrating with your scraper)
#     sample_records = [
#         {
#             "date": "2025-07-19",
#             "penalty_id": "PMS-835143255-25",
#             "district": "Faisalabad",
#             "office": "Tehsil Office, Chak Jhumra",
#             "penalty_type": "Open Heaps",
#             "sub_type": "Open Heaps",
#             "amount": 2000,
#             "status": "New",
#             "imposed": "-",
#             "contractor": "Muhammad Arsal",
#             "added_by": "Qaisar Anwar",
#             "latlong": "31.6446623,73.146669",
#             "created_datetime": "Jul 19, 2025, 10:54:01 AM"
#         },
#         # Add more rows here...
#     ]

#     summary = {
#         "date": "2025-07-19",
#         "total_penalties": 5,
#         "total_amount": 10000,
#         "breakdown": "Open Heaps: 3, Uniform: 2"
#     }

#     insert_penalty_records(sample_records, summary)











# import sqlite3

# conn = sqlite3.connect('suthra_dashboard.db')
# cursor = conn.cursor()

# cursor.execute("DROP TABLE IF EXISTS ped_data")

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS ped_data (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         date TEXT,
#         sr_no TEXT,
#         activity TEXT,
#         key_factor TEXT,
#         base_value TEXT,
#         result TEXT,
#         total_score TEXT,
#         obtained_score TEXT
#     )
# ''')

# cursor.execute('''
#     INSERT INTO ped_data (date, sr_no, activity, key_factor, base_value, result, total_score, obtained_score)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
# ''', (
#     'Jul 19, 2025',
#     '1',
#     'Attendance',
#     'Proper Marking',
#     'Yes',
#     'Yes',
#     '100.00',
#     '100.00'
# ))

# conn.commit()
# conn.close()
# print("✅ PED table created and test data inserted.")


# import sqlite3
# import json

# # Connect to your local database
# conn = sqlite3.connect("dashboard_data.db")
# cursor = conn.cursor()

# # Fetch the most recent PED entry
# cursor.execute("SELECT date, obtained_score, total_score, summary FROM ped_data ORDER BY id DESC LIMIT 1")
# row = cursor.fetchone()

# if row:
#     date, obtained_score, total_score, summary = row
#     print(f"\n🗓️ Date: {date}")
#     print(f"📊 Obtained Score: {obtained_score}")
#     print(f"📈 Total Score: {total_score}")
#     print("📋 Summary (Under-performing Activities):")

#     try:
#         parsed_summary = json.loads(summary)
#         if parsed_summary:
#             for item in parsed_summary:
#                 print(item)
#         else:
#             print("⚠️ No summary data found.")
#     except Exception as e:
#         print("❌ Error parsing summary JSON:", e)
# else:
#     print("🚫 No PED records found in the database.")

# conn.close()


# reset_container_detail_table.py


import sqlite3

conn = sqlite3.connect("dashboard_data.db")
cursor = conn.cursor()

# Optionally: back up the old table
# cursor.execute("ALTER TABLE container_detail RENAME TO container_detail_backup")

# Drop the faulty table
cursor.execute("DROP TABLE IF EXISTS container_detail")

# Recreate with correct structure
cursor.execute("""
    CREATE TABLE container_detail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        vehicle TEXT,
        collected INTEGER,
        time_count INTEGER
    )
""")

conn.commit()
conn.close()

print("✅ Table container_detail reset with correct schema.")
