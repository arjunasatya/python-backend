# attendance_routes.py
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, date, time, timedelta
from face_cnn import detect_and_recognize_faces
from database import db
import pdfkit
import os
# import db, dsb. jika diperlukan

# Path default wkhtmltopdf di Linux
path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

attendance_bp = Blueprint('attendance_bp', __name__)

@attendance_bp.route('/check-location', methods=['POST'])
def check_location():
    """
    Opsional: validasi jarak di server, 
    tapi kita sudah melakukannya di Flutter.
    """
    # ...
    return jsonify({"message":"Not implemented"}), 200

@attendance_bp.route('/absensi/facerec', methods=['POST'])
def facerec():
    try:
        username = request.form.get('username')
        face_file = request.files.get('face_image')
        if not face_file:
            return jsonify({"message": "No file"}), 400

        result = detect_and_recognize_faces(face_file.read())
        predicted_label = result['label']

        # Tergantung logic, recognized = predicted_label == username
        recognized = (predicted_label == username)

        return jsonify({
            "recognized": recognized,
            "label": predicted_label
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@attendance_bp.route('/absensi/submit', methods=['POST'])
def submit_attendance():
    """
    Mencatat absensi setelah wajah dan lokasi diverifikasi.
    """
    try:
        username = request.json.get('username')  # Username login

        # Validasi: Username harus ada
        if not username:
            return jsonify({"message": "Username tidak boleh kosong"}), 400

        cursor = db.cursor(dictionary=True)

        # **Ambil nama dari tabel login_user berdasarkan username**
        cursor.execute("SELECT nama FROM login_user WHERE username = %s", (username,))
        user = cursor.fetchone()

        # Jika user tidak ditemukan
        if not user:
            return jsonify({"message": "User tidak ditemukan"}), 404

        # Ambil nama dari hasil query
        name = user['nama']

        # Ambil waktu sekarang (server)
        now = datetime.now()
        date = now.date()
        time = now.time()

        # Simpan ke database
        sql = "INSERT INTO attendance (username, nama, date, time) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (username, name, date, time))
        db.commit()
        cursor.close()

        return jsonify({"message": "Absensi berhasil dicatat", "status": "success"}), 200

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

    
@attendance_bp.route('/absensi/data', methods=['POST'])
def get_attendance_data():
    """
    Endpoint untuk admin melihat data absensi.
    Menerima JSON: { "username": "<admin_username>" }
    """
    try:
        req_data = request.get_json()
        username = req_data.get('username')
        if not username:
            return jsonify({"message": "Username harus disertakan"}), 400

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT role FROM login_user WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user or user.get('role') != 'admin':
            cursor.close()
            return jsonify({"message": "Akses ditolak. Anda bukan admin"}), 403

        # Query untuk mengambil data absensi
        query = "SELECT username, nama, date, time FROM attendance ORDER BY date DESC, time DESC"
        cursor.execute(query)
        attendance_data = cursor.fetchall()
        
        # Konversi data yang tidak serializable ke string
        for row in attendance_data:
            # Jika 'date' adalah objek date, ubah menjadi string ISO
            if isinstance(row['date'], (date, datetime)):
                row['date'] = row['date'].isoformat()
            # Jika 'time' adalah objek time, ubah menjadi string ISO
            if isinstance(row['time'], time):
                row['time'] = row['time'].isoformat()
            # Jika 'time' adalah objek timedelta, konversi ke format HH:MM:SS
            elif isinstance(row['time'], timedelta):
                total_seconds = int(row['time'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                row['time'] = f"{hours:02}:{minutes:02}:{seconds:02}"

        cursor.close()

        return jsonify({"status": "success", "data": attendance_data}), 200

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

@attendance_bp.route('/absensi/report', methods=['POST'])
def attendance_report():
    """
    Menghasilkan laporan absensi sebagai file PDF.
    Menerima JSON: {
        "username": "<admin_username>",
        "report_type": "harian" / "mingguan" / "bulanan"
    }
    """
    try:
        # Ambil parameter dari request
        report_type = request.json.get("report_type")
        username = request.json.get("username")

        # Validasi admin
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT role FROM login_user WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user or user['role'] != 'admin':
            return jsonify({"message": "Akses ditolak. Anda bukan admin"}), 403

        # Ambil data absensi berdasarkan report_type
        if report_type == "harian":
            query = "SELECT * FROM attendance WHERE date = CURDATE() ORDER BY time DESC"
        elif report_type == "mingguan":
            query = "SELECT * FROM attendance WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) ORDER BY date DESC, time DESC"
        elif report_type == "bulanan":
            query = "SELECT * FROM attendance WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) ORDER BY date DESC, time DESC"
        else:
            return jsonify({"message": "Report type tidak valid."}), 400

        cursor.execute(query)
        attendance_data = cursor.fetchall()
        cursor.close()
        
        # Buat HTML laporan
        html = "<html><head><meta charset='UTF-8'><style>"
        html += "table, th, td { border: 1px solid black; border-collapse: collapse; padding: 5px; }"
        html += "</style></head><body>"
        html += f"<h2>Laporan Absensi - {report_type.upper()}</h2>"
        html += "<table><tr><th>Username</th><th>Nama</th><th>Tanggal</th><th>Waktu</th></tr>"
        for row in attendance_data:
            html += f"<tr><td>{row['username']}</td><td>{row['nama']}</td><td>{row['date']}</td><td>{row['time']}</td></tr>"
        html += "</table></body></html>"

        # Generate PDF menggunakan pdfkit
        pdf_file = f"attendance_report_{report_type}.pdf"
        pdfkit.from_string(html, pdf_file, configuration=config)

        return send_file(pdf_file, as_attachment=True)
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500    