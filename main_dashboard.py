# import tkinter as tk
# from tkinter import ttk
# from tkinter.scrolledtext import ScrolledText
# import sqlite3
# from datetime import datetime
# import threading
# import time

# # --- Constants ---
# REFRESH_INTERVAL = 1800  # 30 minutes in seconds
# DB_PATH = "dashboard_data.db"
# SECTION_CONFIGS = [
#     ("VTCS", "#007BFF"),         # Blue
#     ("VTMS", "#FD7E14"),         # Orange
#     ("Attendance", "#28A745"),   # Green
#     ("PED", "#6F42C1"),          # Purple
#     ("Containers", "#20C997"),   # Teal
#     ("Penalties", "#DC3545"),    # Red
#     ("Waste Summary", "#FFC107"),# Yellow
#     ("System Logs", "#6C757D")   # Gray
# ]

# # --- GUI Setup ---
# root = tk.Tk()
# root.title("Live Monitoring Dashboard - Suthra Punjab")
# root.geometry("1400x900")
# root.configure(bg='white')

# # --- Title ---
# title_label = tk.Label(
#     root,
#     text="LIVE MONITORING - SUTHRA PUNJAB",
#     font=("Segoe UI", 24, "bold"),
#     bg="white",
#     fg="#1c3c6e"
# )
# title_label.pack(pady=(20, 5))

# # --- Last Updated Label ---
# last_updated_label = tk.Label(
#     root,
#     text="Last Updated: --",
#     font=("Segoe UI", 10),
#     bg="white",
#     fg="gray"
# )
# last_updated_label.pack(pady=(0, 10))

# # --- Dashboard Grid Frame ---
# dashboard_frame = tk.Frame(root, bg="white")
# dashboard_frame.pack(padx=30, pady=20, fill="both", expand=True)

# section_widgets = {}

# # --- Section Builder ---
# def create_card(parent, title, color, row, col):
#     card = tk.Frame(
#         parent,
#         bg="white",
#         highlightbackground=color,
#         highlightthickness=2,
#         bd=0,
#         relief="flat"
#     )
#     card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

#     # Icon Placeholder
#     icon = tk.Label(card, text="🗂️", font=("Segoe UI Emoji", 28), bg="white")
#     icon.pack(pady=(10, 0))

#     # Title
#     heading = tk.Label(
#         card, text=title.upper(), font=("Segoe UI", 14, "bold"), bg="white", fg=color
#     )
#     heading.pack(pady=(5, 5))

#     # Summary Box
#     summary = ScrolledText(
#         card, height=6, wrap="word", font=("Segoe UI", 10), bg="#f9f9f9", relief="flat"
#     )
#     summary.pack(fill="both", expand=True, padx=10, pady=(0, 10))
#     summary.insert(tk.END, "Loading...")
#     summary.config(state="disabled")

#     # Footer Buttons
#     footer = tk.Frame(card, bg="white")
#     footer.pack(pady=(0, 10))

#     detail_btn = tk.Button(
#         footer, text="📄 Detail", command=lambda: show_detail(title), font=("Segoe UI", 9), bg="white", fg=color
#     )
#     detail_btn.pack(side="left", padx=10)

#     refresh_btn = tk.Button(
#         footer, text="🔄 Refresh", command=lambda: refresh_section(title), font=("Segoe UI", 9), bg="white", fg=color
#     )
#     refresh_btn.pack(side="right", padx=10)

#     section_widgets[title] = summary

# # --- Show Details ---
# def show_detail(section):
#     detail_window = tk.Toplevel(root)
#     detail_window.title(f"{section} Details")
#     detail_window.geometry("900x600")
#     detail_text = ScrolledText(detail_window, font=("Consolas", 10))
#     detail_text.pack(fill="both", expand=True)
#     try:
#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()

#         if section == "VTCS":
#             cursor.execute("SELECT date, collected_kg FROM vtcs_data ORDER BY id DESC LIMIT 10")
#             for row in cursor.fetchall():
#                 detail_text.insert(tk.END, f"{row[0]} - {row[1]} Kg\n")

#         elif section == "VTMS":
#             cursor.execute("SELECT date, active_count, inactive_count FROM vtms_data ORDER BY id DESC LIMIT 10")
#             for row in cursor.fetchall():
#                 detail_text.insert(tk.END, f"{row[0]} - Active: {row[1]} | Inactive: {row[2]}\n")

#         elif section == "Attendance":
#             cursor.execute("SELECT summary FROM attendance_data ORDER BY id DESC LIMIT 1")
#             row = cursor.fetchone()
#             detail_text.insert(tk.END, row[0] if row else "No data")

#         elif section == "PED":
#             cursor.execute("SELECT summary FROM ped_data ORDER BY id DESC LIMIT 1")
#             row = cursor.fetchone()
#             detail_text.insert(tk.END, row[0] if row else "No data")

#         elif section == "Containers":
#             cursor.execute("SELECT date, count FROM container_data ORDER BY id DESC LIMIT 10")
#             for row in cursor.fetchall():
#                 detail_text.insert(tk.END, f"{row[0]} - Count: {row[1]}\n")

#         elif section == "Penalties":
#             cursor.execute("SELECT date, total_penalties, total_amount, breakdown FROM penalties_data ORDER BY id DESC LIMIT 10")
#             for row in cursor.fetchall():
#                 detail_text.insert(tk.END, f"{row[0]} - Penalties: {row[1]}, Amount: Rs.{row[2]}\n{row[3]}\n\n")

#         conn.close()
#     except Exception as e:
#         detail_text.insert(tk.END, str(e))

# # --- Refresh Section ---
# def refresh_section(title):
#     print(f"[REFRESH] {title} triggered")
#     update_last_updated()

# # --- Update Last Updated Label ---
# def update_last_updated():
#     last_updated_label.config(text=f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# # --- Build Layout ---
# dashboard_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
# for i, (name, color) in enumerate(SECTION_CONFIGS):
#     create_card(dashboard_frame, name, color, i//4, i%4)

# # --- Auto Refresh Thread ---
# def auto_refresh():
#     while True:
#         time.sleep(REFRESH_INTERVAL)
#         for name, _ in SECTION_CONFIGS:
#             refresh_section(name)

# threading.Thread(target=auto_refresh, daemon=True).start()

# update_last_updated()
# root.mainloop()

# === NEW WEB-BASED DASHBOARD (FLASK) ===
# File: app.py

from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_PATH = "dashboard_data.db"

# --- Routes ---
@app.route("/")
def dashboard():
    data = {}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # VTCS
        cursor.execute("SELECT date, collected_kg FROM vtcs_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        data["VTCS"] = f"{row[0]}: {row[1]} Kg Collected" if row else "No data"

        # VTMS
        cursor.execute("SELECT date, active_count, inactive_count FROM vtms_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        data["VTMS"] = f"{row[0]}: 🟢 {row[1]} Active / 🔴 {row[2]} Inactive" if row else "No data"

        # Attendance
        cursor.execute("SELECT date, summary FROM attendance_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        data["Attendance"] = row[1][:200] + "..." if row else "No data"

        # PED
        cursor.execute("SELECT date, summary FROM ped_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        data["PED"] = row[1][:200] + "..." if row else "No data"

        # Containers
        cursor.execute("SELECT date, count FROM container_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        data["Containers"] = f"{row[0]}: {row[1]} container services logged" if row else "No data"

        # Penalties
        cursor.execute("SELECT date, total_penalties, total_amount FROM penalties_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        data["Penalties"] = f"{row[0]}: {row[1]} penalties, Rs. {row[2]:,.0f}" if row else "No data"

    except Exception as e:
        data["error"] = str(e)

    conn.close()

    return render_template("dashboard.html", data=data, last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# --- API for Section Detail (AJAX Modal) ---
@app.route("/detail/<section>")
def detail(section):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    result = []

    try:
        if section == "VTCS":
            cursor.execute("SELECT date, collected_kg FROM vtcs_data ORDER BY id DESC LIMIT 10")
            result = cursor.fetchall()
        elif section == "VTMS":
            cursor.execute("SELECT date, active_count, inactive_count FROM vtms_data ORDER BY id DESC LIMIT 10")
            result = cursor.fetchall()
        elif section == "Attendance":
            cursor.execute("SELECT summary FROM attendance_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            result = row[0].splitlines() if row else []
        elif section == "PED":
            cursor.execute("SELECT summary FROM ped_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            result = row[0].splitlines() if row else []
        elif section == "Containers":
            cursor.execute("SELECT date, count FROM container_data ORDER BY id DESC LIMIT 10")
            result = cursor.fetchall()
        elif section == "Penalties":
            cursor.execute("SELECT date, total_penalties, total_amount, breakdown FROM penalties_data ORDER BY id DESC LIMIT 10")
            result = cursor.fetchall()
    except Exception as e:
        result = [str(e)]

    conn.close()
    return jsonify(result)

# --- Run Server ---
if __name__ == "__main__":
    app.run(debug=True)
