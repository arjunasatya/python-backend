# database.py
import mysql.connector

db = mysql.connector.connect(
    host='127.0.0.1',
    user='flask_user',
    password='password123',
    database='absensi'
)
