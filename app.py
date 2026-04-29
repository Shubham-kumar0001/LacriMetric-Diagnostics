import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
import uuid
from flask import Flask, request, jsonify, render_template, session
from camera import process_video_file

app = Flask(__name__)
app.secret_key = "secure_medical_key"
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Mock Database for Doctor System
db = {
    "doctors": {"admin": "password123"},
    "reports": []
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in db["doctors"] and db["doctors"][username] == password:
        session['doctor_logged_in'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('doctor_logged_in', None)
    return jsonify({"success": True})

@app.route('/api/auth_status', methods=['GET'])
def auth_status():
    return jsonify({"logged_in": session.get('doctor_logged_in', False)})

@app.route('/api/reports', methods=['GET'])
def get_reports():
    if not session.get('doctor_logged_in', False):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(db["reports"])

@app.route('/process', methods=['POST'])
def handle_process_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
        
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "Empty file uploaded"}), 400
        
    ext = file.filename.split('.')[-1]
    if ext == 'blob' or ext == '':
        ext = 'webm'
        
    filename = str(uuid.uuid4()) + f".{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        frontend_duration = request.form.get('duration', type=float)
        results = process_video_file(filepath, frontend_duration=frontend_duration)
        os.remove(filepath)
        
        if "error" in results:
            return jsonify(results), 400
            
        # Add to Doctor DB
        results['id'] = str(uuid.uuid4())[:8]
        db["reports"].insert(0, results)
        
        return jsonify(results)
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": f"Processing Runtime Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
