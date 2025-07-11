from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from pymongo import MongoClient
import re
import subprocess
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# --- SQLite Setup ---
def get_db_connection():
    conn = sqlite3.connect('medical_maestro.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_tables():
    conn = get_db_connection()
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Patients table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            dob TEXT,
            pre_existing_conditions TEXT,
            allergies TEXT,
            current_medications TEXT
        )
    ''')
    # Appointments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            patient_name TEXT NOT NULL
        )
    ''')
    # llm_server_ip table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS llm_server_ip (
            id INTEGER PRIMARY KEY,
            ip VARCHAR(15) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database tables
init_sqlite_tables()

# --- MongoDB Setup ---
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["medical_maestro"]
files_collection = mongo_db["patient_files"]

# --- Endpoints ---
@app.route('/')
@app.route('/login')
def login_page():
    return app.send_static_file('medical_login_screen.html')

@app.route('/welcome')
def welcome_page():
    return app.send_static_file('welcome_screen.html')

@app.route('/patient')
def patient_page():
    return app.send_static_file('patient_screen.html')

@app.route('/test-results')
def test_results_page():
    return app.send_static_file('medical_test_results.html')

@app.route('/appointments')
def appointments_page():
    return app.send_static_file('appointments_screen.html')

@app.route('/add-appointment')
def add_appointment_page():
    return app.send_static_file('add_appointment.html')

@app.route('/add-patient')
def add_patient_page():
    return app.send_static_file('add_patient.html')

@app.route('/add-user')
def add_user_page():
    return app.send_static_file('add_user.html')

@app.route('/admin')
def admin_dashboard():
    return app.send_static_file('admin_dashboard.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    if user:
        return jsonify({'success': True, 'full_name': user['full_name']})
    else:
        return jsonify({'success': False}), 401

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    try:
        conn = get_db_connection()
        print("Fetching appointments from database...")  # Debug log
        
        # First, let's check if the appointments table exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments'")
        if not cursor.fetchone():
            print("Appointments table does not exist!")  # Debug log
            conn.close()
            return jsonify([])
            
        appointments = conn.execute('SELECT time, patient_name FROM appointments').fetchall()
        print(f"Found {len(appointments)} appointments")  # Debug log
        
        result = [{'time': row['time'], 'patient_name': row['patient_name']} for row in appointments]
        print(f"Returning appointments: {result}")  # Debug log
        
        conn.close()
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching appointments: {str(e)}")  # Debug log
        return jsonify({'error': f'Failed to fetch appointments: {str(e)}'}), 500

@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    try:
        data = request.get_json()
        time = data.get('time')
        patient_name = data.get('patient_name')
        
        if not (time and patient_name):
            return jsonify({'error': 'Time and patient name are required.'}), 400
            
        print(f"Adding appointment - Time: {time}, Patient: {patient_name}")  # Debug log
        
        conn = get_db_connection()
        cursor = conn.execute('INSERT INTO appointments (time, patient_name) VALUES (?, ?)', (time, patient_name))
        conn.commit()
        print(f"Appointment added with ID: {cursor.lastrowid}")  # Debug log
        conn.close()
        
        return jsonify({'success': True, 'message': 'Appointment added successfully'})
    except Exception as e:
        print(f"Error adding appointment: {str(e)}")  # Debug log
        return jsonify({'error': f'Failed to add appointment: {str(e)}'}), 500

# Example endpoint for MongoDB files (expand as needed)
@app.route('/patient_files', methods=['GET'])
def get_patient_files():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    files = list(files_collection.find({'name': name}, {'_id': 0}))
    return jsonify(files)

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT full_name, username FROM users').fetchall()
    conn.close()
    return jsonify([{'full_name': row['full_name'], 'username': row['username']} for row in users])

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    full_name = data.get('full_name')
    username = data.get('username')
    password = data.get('password')
    if not (full_name and username and password):
        return jsonify({'error': 'All fields are required.'}), 400
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (full_name, username, password) VALUES (?, ?, ?)',
                     (full_name, username, password))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists.'}), 400

@app.route('/patients', methods=['GET'])
def get_patients():
    conn = get_db_connection()
    patients = conn.execute('SELECT name, gender, dob, pre_existing_conditions, allergies, current_medications FROM patients').fetchall()
    conn.close()
    return jsonify([
        {
            'name': row['name'],
            'gender': row['gender'],
            'dob': row['dob'],
            'pre_existing_conditions': row['pre_existing_conditions'],
            'allergies': row['allergies'],
            'current_medications': row['current_medications']
        } for row in patients
    ])

@app.route('/patients', methods=['POST'])
def add_patient():
    data = request.get_json()
    name = data.get('name')
    gender = data.get('gender')
    dob = data.get('dob')
    pre_existing_conditions = data.get('pre_existing_conditions')
    allergies = data.get('allergies')
    current_medications = data.get('current_medications')
    if not (name and gender and dob):
        return jsonify({'error': 'Name, Gender, and DOB are required.'}), 400
    conn = get_db_connection()
    conn.execute('INSERT INTO patients (name, gender, dob, pre_existing_conditions, allergies, current_medications) VALUES (?, ?, ?, ?, ?, ?)',
                 (name, gender, dob, pre_existing_conditions, allergies, current_medications))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/patients/by_name', methods=['GET'])
def get_patient_by_name():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    conn = get_db_connection()
    patient = conn.execute('SELECT name, gender, dob, pre_existing_conditions, allergies, current_medications FROM patients WHERE name = ?', (name,)).fetchone()
    conn.close()
    if patient:
        return jsonify({
            'name': patient['name'],
            'gender': patient['gender'],
            'dob': patient['dob'],
            'pre_existing_conditions': patient['pre_existing_conditions'],
            'allergies': patient['allergies'],
            'current_medications': patient['current_medications']
        })
    else:
        return jsonify({'error': 'Patient not found.'}), 404

@app.route('/llm-server')
def llm_server():
    return app.send_static_file('llm_server.html')

@app.route('/api/llm-server-ip', methods=['GET'])
def get_llm_server_ip():
    try:
        conn = get_db_connection()
        cursor = conn.execute('SELECT ip FROM llm_server_ip WHERE id = 1')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({'ip': result[0]})
        else:
            return jsonify({'ip': None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/llm-server-ip', methods=['POST'])
def update_llm_server_ip():
    try:
        data = request.get_json()
        if not data or 'ip' not in data:
            return jsonify({'error': 'IP address is required'}), 400
            
        ip = data['ip']
        # Basic IP validation
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
            return jsonify({'error': 'Invalid IP address format'}), 400
            
        conn = get_db_connection()
        
        # Check if record exists
        cursor = conn.execute('SELECT id FROM llm_server_ip WHERE id = 1')
        if cursor.fetchone():
            conn.execute('UPDATE llm_server_ip SET ip = ? WHERE id = 1', (ip,))
        else:
            conn.execute('INSERT INTO llm_server_ip (id, ip) VALUES (1, ?)', (ip,))
            
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'IP address updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chatbot')
def chatbot():
    return app.send_static_file('chatbot.html')



# New endpoint to trigger backend processing
@app.route('/api/trigger-backend', methods=['POST'])
def trigger_backend():
    try:
        data = request.get_json()
        patient_name = data.get('patient_name')
        
        if not patient_name:
            return jsonify({'error': 'Patient name is required.'}), 400
            
        # Path to the backend application (backend files are in the same directory)
        backend_path = '.'  # Backend files are in the current directory
        
        # Check if backend application exists
        if not os.path.exists(backend_path):
            return jsonify({'error': 'Backend application not found.'}), 404
            
        # Trigger the backend application
        # Try different possible entry points
        entry_points = ['main.py', 'app.py', 'run.py', '__main__.py']
        backend_script = None
        
        for entry_point in entry_points:
            potential_script = os.path.join(backend_path, entry_point)
            if os.path.exists(potential_script):
                backend_script = potential_script
                break
        
        if not backend_script:
            return jsonify({'error': 'No backend entry point found (main.py, app.py, run.py, or __main__.py)'}), 404
        
        result = subprocess.run([
            'python', backend_script, 
            '--patient', patient_name
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            return jsonify({
                'success': True, 
                'message': 'Backend processing completed successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Backend processing failed',
                'details': result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Backend processing timed out'}), 408
    except Exception as e:
        return jsonify({'error': f'Failed to trigger backend: {str(e)}'}), 500

# Enhanced endpoint to get patient files with dates and LLM summaries
@app.route('/api/patient-test-results', methods=['GET'])
def get_patient_test_results():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Name is required.'}), 400
        
    try:
        # Get all test results for the patient, sorted by date
        files = list(files_collection.find(
            {'name': name}
        ).sort('date_processed', -1))
        
        # Group by date and format for frontend
        results_by_date = {}
        for file_record in files:
            date_key = file_record.get('date_processed', 'Unknown Date')
            if date_key not in results_by_date:
                results_by_date[date_key] = {
                    'date': date_key,
                    'files': [],
                    'llm_summary': file_record.get('llm_summary', '')
                }
            
            # Add individual test files
            for test_type in ['Blood Test', 'CT Scan', 'MRI', 'Urine', 'Stool']:
                if file_record.get(test_type):
                    # Convert ObjectId to string for URL
                    record_id = str(file_record.get('_id', '')) if file_record.get('_id') else ''
                    results_by_date[date_key]['files'].append({
                        'type': test_type,
                        'filename': file_record[test_type].split('/')[-1] if '/' in file_record[test_type] else file_record[test_type],
                        'download_url': f"/api/download-pdf/{record_id}/{test_type.replace(' ', '_')}"
                    })
        
        # Convert to list and sort by date (most recent first)
        sorted_results = list(results_by_date.values())
        sorted_results.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(sorted_results)
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch test results: {str(e)}'}), 500

# Endpoint to download PDF files
@app.route('/api/download-pdf/<record_id>/<test_type>')
def download_pdf(record_id, test_type):
    try:
        from bson import ObjectId
        
        # Convert test_type back from URL format
        test_type_original = test_type.replace('_', ' ')
        
        # Find the file record in MongoDB
        try:
            file_record = files_collection.find_one({'_id': ObjectId(record_id)})
        except:
            # If ObjectId conversion fails, try as string
            file_record = files_collection.find_one({'_id': record_id})
            
        if not file_record:
            return jsonify({'error': 'File record not found'}), 404
            
        # Get the file path for the requested test type
        file_path = file_record.get(test_type_original)
        if not file_path:
            return jsonify({'error': f'No {test_type_original} file found for this record'}), 404
            
        # Check if file exists on disk
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on disk'}), 404
            
        # Serve the file for download
        from flask import send_file
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)