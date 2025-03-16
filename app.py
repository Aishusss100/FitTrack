from flask import Flask, request, jsonify, session, redirect, url_for, Response
from flask_cors import CORS
import sqlite3
from exercise_tracker import (
    init_exercise_tracker, 
    get_exercise_data, 
    change_exercise, 
    set_target_reps, 
    start_exercise,
    stop_exercise,
    generate_video_frames
)

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
app.secret_key = 'your_secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Helps with CORS issues
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

# Initialize exercise tracker
init_exercise_tracker()

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            name TEXT,
            date_of_birth TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# New endpoint to check session status
@app.route('/api/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({'logged_in': True, 'username': session['username']})
    else:
        return jsonify({'logged_in': False})

# API endpoint for user login
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        session['username'] = username
        session.modified = True  # Ensure the session is saved
        print(f"Session set in login: {session}")
        print(f"Session ID: {request.cookies.get('session')}")
        init_exercise_tracker()  # Reset exercise counters on login
        return jsonify({'message': 'Login successful', 'username': username})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# API endpoint for user logout
@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    return jsonify({'message': 'Logout successful'})

# API endpoint for user signup
@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    date_of_birth = data.get('dateOfBirth')
    email = data.get('email')
    print(f"Received signup request: username={username}, password={password}, name={name}, date_of_birth={date_of_birth}, email={email}")

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (username, password, name, date_of_birth, email) 
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password, name, date_of_birth, email))
        conn.commit()
        print("User added successfully.")
        return jsonify({'message': 'Signup successful'})
    except sqlite3.IntegrityError as e:
        print("IntegrityError:", e)
        return jsonify({'message': 'Username already taken'}), 409
    except sqlite3.Error as e:
        print("SQLite Error:", e)
        return jsonify({'message': 'Database error'}), 500
    finally:
        conn.close()

@app.route('/api/profile', methods=['GET'])
def get_profile():
    # Debugging: Check session data
    print(f"Session data at /api/profile: {session}")
    print(f"Session cookie: {request.cookies.get('session')}")

    # Verify if the user is logged in by checking the session
    if 'username' not in session:
        print("User not logged in - session['username'] missing")
        return jsonify({'message': 'User not logged in'}), 401

    # Retrieve username from the session
    username = session['username']
    print(f"Fetching profile for username: {username}")  # Debugging

    # Query the database for the user's details
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT username, name, date_of_birth, email FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    # Check if user exists in the database
    if user:
        print(f"User data found: {user}")  # Debugging
        return jsonify({
            'username': user[0],
            'name': user[1],
            'date_of_birth': user[2],
            'email': user[3]
        })
    else:
        print("User not found in database")  # Debugging
        return jsonify({'message': 'User not found'}), 404

# API endpoint for getting exercise data
@app.route('/api/exercises', methods=['GET'])
def get_exercises():
    return jsonify(get_exercise_data())

# API endpoint for changing the current exercise
@app.route('/api/change_exercise', methods=['POST'])
def api_change_exercise():
    data = request.get_json()
    exercise = data.get('exercise')
    result = change_exercise(exercise)
    if result['success']:
        return jsonify({'message': 'Exercise changed successfully'})
    else:
        return jsonify({'message': 'Invalid exercise'}), 400

# API endpoint for setting the target
@app.route('/api/set_target', methods=['POST'])
def set_target():
    data = request.get_json()
    target_reps = data.get('target_reps', 0)
    result = set_target_reps(target_reps)
    return jsonify({'message': 'Target set successfully', 'target_reps': result['target_reps']})

# API endpoint for starting the exercise
@app.route('/api/start', methods=['POST'])
def start_exercise_route():
    result = start_exercise()
    return jsonify({'message': 'Exercise started'})

# API endpoint for stopping the exercise
@app.route('/api/stop', methods=['POST'])
def stop_exercise_route():
    result = stop_exercise()
    return jsonify({'message': 'Exercise stopped'})

# Video feed endpoint
@app.route('/api/video_feed')
def video_feed():
    return Response(generate_video_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)