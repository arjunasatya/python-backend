from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.attendance_routes import attendance_bp

# Import blueprint lain jika ada

app = Flask(__name__)
CORS(app)

# Registrasi blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(attendance_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
