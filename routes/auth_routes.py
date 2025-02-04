# python_backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify, session
import mysql.connector
from database import db
auth_bp = Blueprint('auth_bp', __name__)

# Asumsi koneksi DB telah diinisialisasi di app.py
# Kita butuh cara import db, misalnya:

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        nama = data.get('nama')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not all([nama, email, username, password]):
            return jsonify({"message": "Data tidak lengkap"}), 400

        cursor = db.cursor(dictionary=True)

        # Cek apakah username/email sudah ada
        sql_check = "SELECT * FROM login_user WHERE username=%s OR email=%s"
        cursor.execute(sql_check, (username, email))
        existing = cursor.fetchall()
        if len(existing) > 0:
            return jsonify({"message": "Username atau Email sudah terdaftar"}), 400

        # Insert data
        sql_insert = """INSERT INTO login_user (nama, email, username, password)
                        VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql_insert, (nama, email, username, password))
        db.commit()
        cursor.close()

        return jsonify({"message": "Registrasi berhasil"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not all([username, password]):
            return jsonify({"message": "Masukkan username dan password"}), 400

        cursor = db.cursor(dictionary=True)
        sql = "SELECT * FROM login_user WHERE username=%s AND password=%s"
        cursor.execute(sql, (username, password))
        user_data = cursor.fetchall()
        cursor.close()
        if len(user_data) == 0:
            return jsonify({"message": "Username atau password salah"}), 401

        user = user_data[0]
        return jsonify({
            "message": "Login berhasil",
            "user": {
                "nama": user['nama'],
                "username": user['username'],
                "role": user['role']
            }
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user (jika menggunakan session Flask).
    """
    session.clear()  # Hapus sesi
    return jsonify({"message": "Logout berhasil"}), 200