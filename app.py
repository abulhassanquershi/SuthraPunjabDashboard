from flask import Flask, render_template, jsonify, send_file
import sqlite3
import pandas as pd
from io import BytesIO
import json
from datetime import datetime
from vtcs_scraper import get_vtcs_summary, get_vtcs_details
from vtms_scraper import get_vtms_summary, get_vtms_details

app = Flask(__name__)
DB_PATH = "dashboard_data.db"

@app.route("/")
def dashboard():
    ped_score = "No PED data"
    attendance_summary = "No Attendance Data"
    container_summary = "No Container Data"
    penalty_summary = "No Penalty Data"

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT obtained_score, total_score FROM ped_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            ped_score = f"{row[0]:.1f} / {row[1]:.1f}"

        cursor.execute("SELECT summary FROM attendance_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            attendance_summary = row[0]

        cursor.execute("SELECT count, urban, rural FROM container_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            total, urban, rural = row
            container_summary = f"📦 Total: {total} | 🌆 Urban: {urban} | 🌄 Rural: {rural}"

        cursor.execute("SELECT date, count, total_amount FROM penalties_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            date_str, count, total_amount = row
            penalty_summary = f"📅 {date_str} | 💸 Penalties: {count} | Rs. {total_amount:.0f}"

        conn.close()
    except Exception as e:
        ped_score = f"❌ PED error: {e}"

    # Last Updated Timestamp
    last_updated = "N/A"
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(date) FROM (
                SELECT date FROM vtcs_data
                UNION ALL SELECT date FROM vtms_data
                UNION ALL SELECT date FROM ped_data
                UNION ALL SELECT date FROM attendance_data
                UNION ALL SELECT date FROM container_data
                UNION ALL SELECT date FROM penalties_data
            )
        """)
        row = cursor.fetchone()
        if row and row[0]:
            try:
                parsed = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                last_updated = parsed.strftime("%d-%b-%Y %I:%M %p")
            except:
                try:
                    parsed = datetime.strptime(row[0], "%Y-%m-%d")
                    last_updated = parsed.strftime("%d-%b-%Y") + " " + datetime.now().strftime("%I:%M %p")
                except:
                    last_updated = row[0]
        else:
            last_updated = datetime.now().strftime("%d-%b-%Y %I:%M %p")
        conn.close()
    except:
        last_updated = datetime.now().strftime("%d-%b-%Y %I:%M %p")

    data = {
        "VTCS": get_vtcs_summary(),
        "VTMS": get_vtms_summary(),
        "PED": ped_score,
        "Attendance": attendance_summary,
        "Container": container_summary,
        "Penalties": penalty_summary
    }

    return render_template("dashboard.html", data=data, last_updated=last_updated)

@app.route("/container-detail")
def container_detail():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT date FROM container_data ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return "No container data found."
        date_str = row[0]

        cursor.execute("SELECT id, date, vehicle, collected FROM container_detail WHERE date = ?", (date_str,))
        rows = cursor.fetchall()
        conn.close()

        return render_template("container_detail.html", rows=rows)

    except Exception as e:
        return f"Error loading container detail: {str(e)}"

@app.route("/detail/<section>")
def detail(section):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if section.lower() == "vtcs":
            return jsonify(get_vtcs_details())

        elif section.lower() == "vtms":
            return jsonify(get_vtms_details())

        elif section.lower() == "ped":
            cursor.execute("SELECT obtained_score, total_score, summary FROM ped_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if not row:
                return jsonify([{"info": "No PED data found."}])
            obtained_score = float(row[0])
            total_score = float(row[1])
            summary_json = row[2]

            if obtained_score == total_score:
                return jsonify([{
                    "info": f"✅ Congratulations! You scored {int(obtained_score)}/{int(total_score)}."
                }])

            try:
                summary = json.loads(summary_json)
                under_performing = []
                for item in summary:
                    score_str = item.get("Score", "0.0/0.0")
                    obtained, total = map(float, score_str.split("/"))
                    if obtained < total:
                        under_performing.append(item)
                if under_performing:
                    return jsonify(under_performing)
                else:
                    return jsonify([{"info": "No under-performing activities found."}])
            except Exception as e:
                return jsonify([{"error": f"Error parsing PED data: {str(e)}"}])

        elif section.lower() == "attendance":
            cursor.execute("SELECT absent_detail FROM attendance_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if row and row[0]:
                return jsonify([{"__html__": row[0]}])
            else:
                return jsonify([{"info": "No absent data available."}])

        elif section.lower() == "container":
            cursor.execute("SELECT date, count, urban, rural FROM container_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if not row:
                conn.close()
                return jsonify([{"info": "No container data available."}])
            date_str, total, urban, rural = row

            cursor.execute("SELECT vehicle, collected FROM container_detail WHERE date = ?", (date_str,))
            vehicle_rows = cursor.fetchall()
            conn.close()

            response = [{
                "Date": date_str,
                "Total Containers": total,
                "Urban": urban,
                "Rural": rural
            }]

            if vehicle_rows:
                response.append({"__separator__": True})
                for vehicle, collected in vehicle_rows:
                    response.append({
                        "Vehicle": vehicle,
                        "Collected": collected
                    })

            return jsonify(response)

        elif section.lower() == "penalties":
            cursor.execute("SELECT date, details_json FROM penalties_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if not row:
                return jsonify([{"info": "No penalty data available."}])
            date_str, details_json = row
            try:
                if details_json:
                    parsed_data = json.loads(details_json)
                    if isinstance(parsed_data, list) and parsed_data:
                        for item in parsed_data:
                            imposed = item.get("Imposed", "").strip().lower()
                            if imposed and imposed not in ['-', 'no', 'n', 'none']:
                                item["__row_class__"] = "text-danger"
                        return jsonify(parsed_data)
                    else:
                        return jsonify([{"info": "No penalties found."}])
                else:
                    return jsonify([{"info": "No detailed penalties recorded."}])
            except Exception as e:
                return jsonify([{"error": f"Error parsing penalty details: {str(e)}"}])

        return jsonify([{"info": f"No data found for section: {section}"}])

    except Exception as e:
        return jsonify({"error": f"Failed to load detail for {section}: {str(e)}"})

@app.route("/download/attendance")
def download_attendance_excel():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("""
            SELECT date, summary, absent_detail
            FROM attendance_data ORDER BY id DESC LIMIT 1
        """, conn)
        conn.close()

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance Summary')

        output.seek(0)
        return send_file(output, as_attachment=True,
                         download_name="attendance_summary.xlsx",
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
