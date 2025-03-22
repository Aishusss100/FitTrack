from flask import Flask, request, jsonify, session, redirect, url_for, Response
from flask_cors import CORS
import sqlite3
from datetime import date, timedelta

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
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

# Initialize exercise tracker
init_exercise_tracker()

# Initialize user database
def init_user_db():
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

# Initialize progress tracking database
def init_progress_db():
    conn = sqlite3.connect('exercise_progress_with_duration.db')  # Updated database name
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS exercise_progress_with_duration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            date DATE NOT NULL,
            reps INTEGER DEFAULT 0,
            duration INTEGER DEFAULT 0, -- New column to store duration in seconds
            UNIQUE(username, exercise_name, date) ON CONFLICT REPLACE
        );
    ''')
    conn.commit()
    conn.close()


# Initialize both databases
init_user_db()
init_progress_db()

# User authentication APIs
@app.route('/api/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({'logged_in': True, 'username': session['username']})
    else:
        return jsonify({'logged_in': False})

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
        session.modified = True
        init_exercise_tracker()
        return jsonify({'message': 'Login successful', 'username': username})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    date_of_birth = data.get('dateOfBirth')
    email = data.get('email')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (username, password, name, date_of_birth, email) 
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password, name, date_of_birth, email))
        conn.commit()
        return jsonify({'message': 'Signup successful'})
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already taken'}), 409
    finally:
        conn.close()
        

@app.route('/api/profile', methods=['GET'])
def get_profile():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    username = session['username']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT username, name, date_of_birth, email FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({
            'username': user[0],
            'name': user[1],
            'date_of_birth': user[2],
            'email': user[3]
        })
    else:
        return jsonify({'message': 'User not found'}), 404

# Exercise tracking APIs
# @app.route('/api/exercises', methods=['GET'])
# def get_exercises():
#     return jsonify(get_exercise_data())

@app.route('/api/change_exercise', methods=['POST'])
def api_change_exercise():
    data = request.get_json()
    exercise = data.get('exercise')
    result = change_exercise(exercise)
    if result['success']:
        return jsonify({'message': 'Exercise changed successfully'})
    else:
        return jsonify({'message': 'Invalid exercise'}), 400

@app.route('/api/set_target', methods=['POST'])
def set_target():
    data = request.get_json()
    target_reps = data.get('target_reps', 0)
    result = set_target_reps(target_reps)
    return jsonify({'message': 'Target set successfully', 'target_reps': result['target_reps']})

@app.route('/api/start', methods=['POST'])
def start_exercise_route():
    data = request.get_json()
    exercise_name = data.get('exercise')  # Get the exercise name from the frontend

    # Call the start_exercise function with the selected exercise
    result = start_exercise(exercise_name)
    return jsonify(result)


@app.route('/api/stop', methods=['POST'])
def stop_exercise_route():
    data = request.get_json()
    duration = data.get('duration', 0)  # Timer data from frontend
    
    # Stop the exercise and get the exercise data
    stop_result = stop_exercise()
    
    if stop_result.get('success'):
        exercise_data = stop_result.get('exercise_data', {})
        exercise_name = exercise_data.get('exercise_name')
        reps = exercise_data.get('reps', 0)
        
        # Update the progress in the database
        update_payload = {
            'exercise_name': exercise_name,
            'duration': duration,
            'reps': reps
        }
        response = update_progress_internal(update_payload)
        return jsonify(response)
    else:
        return jsonify({'message': 'Failed to stop exercise'}), 500

@app.route('/api/video_feed')
def video_feed():
    return Response(generate_video_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/api/get_username', methods=['GET'])
def get_username():
    username = session.get('username', None)
    if not username:
        return jsonify({'message': 'User not logged in'}), 401
    return jsonify({'username': username})

def update_progress_internal(data):
    username = session.get('username')
    if not username:
        return {'message': 'User not logged in', 'success': False}

    exercise_name = data.get('exercise_name')
    reps = data.get('reps', 0)
    duration = data.get('duration', 0)  # Duration in seconds
    today = str(date.today())

    conn = sqlite3.connect('exercise_progress_with_duration.db')  # Use the new table
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO exercise_progress_with_duration (username, exercise_name, date, reps, duration)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username, exercise_name, date)
            DO UPDATE SET 
                reps = reps + ?,
                duration = duration + ?;
        """, (username, exercise_name, today, reps, duration, reps, duration))
        conn.commit()
    except Exception as e:
        print(f"Error updating progress: {e}")
        return {'message': 'Failed to update progress', 'success': False}
    finally:
        conn.close()

    return {'message': 'Progress updated successfully!', 'success': True}

@app.route('/')
def home():
    return "Welcome to the Flask Backend!"

# Progress tracking APIs
@app.route('/api/update_progress', methods=['POST'])
def update_progress():
    data = request.get_json()
    username = session.get('username')
    if not username:
        return jsonify({'message': 'User not logged in'}), 401

    exercise_name = data.get('exercise_name')
    reps = data.get('reps', 0)
    duration = data.get('duration', 0)  # Duration in seconds
    today = str(date.today())

    conn = sqlite3.connect('exercise_progress_with_duration.db')  # Use the new table
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO exercise_progress_with_duration (username, exercise_name, date, reps, duration)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username, exercise_name, date)
            DO UPDATE SET 
                reps = reps + ?,
                duration = duration + ?;
        """, (username, exercise_name, today, reps, duration, reps, duration))
        conn.commit()
    except Exception as e:
        print(f"Error updating progress: {e}")
        return jsonify({'message': 'Failed to update progress'}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Progress updated successfully!'})


@app.route('/api/get_exercises', methods=['GET'])
def get_exercises():
    return jsonify([
        'bicep_curl_left', 'bicep_curl_right',
        'overhead_press_left', 'overhead_press_right',
        'lateral_raise_left', 'lateral_raise_right',
        'front_raise_left', 'front_raise_right',
        'single_arm_dumbbell_left', 'single_arm_dumbbell_right'
    ])


# @app.route('/api/get_progress', methods=['GET'])
# def get_progress():
#     username = session.get('username')
#     if not username:
#         return jsonify({'message': 'User not logged in'}), 401

#     date_filter = request.args.get('date')
#     exercise_name = request.args.get('exercise_name')

#     conn = sqlite3.connect('exercise_progress_with_duration.db')
#     cursor = conn.cursor()
#     try:
#         query = """
#             SELECT exercise_name, reps, duration
#             FROM exercise_progress_with_duration
#             WHERE username = ? AND date = ? AND exercise_name = ?;
#         """
#         cursor.execute(query, (username, date_filter, exercise_name))
#         rows = cursor.fetchall()
#     except Exception as e:
#         print(f"Error fetching progress: {e}")
#         return jsonify({'message': 'Failed to fetch progress'}), 500
#     finally:
#         conn.close()

#     return jsonify([
#         {'exercise_name': row[0], 'reps': row[1], 'duration': row[2]} for row in rows
#     ])

@app.route('/api/get_progress', methods=['GET'])
def get_progress():
    username = session.get('username')
    if not username:
        return jsonify({'message': 'User not logged in'}), 401

    view_type = request.args.get('view_type')  # Accept "daily", "weekly", "monthly"
    exercise_name = request.args.get('exercise_name')

    conn = sqlite3.connect('exercise_progress_with_duration.db')
    cursor = conn.cursor()

    try:
        if view_type == "daily":
            # Fetch progress for today
            query = """
                SELECT date, SUM(reps), SUM(duration)
                FROM exercise_progress_with_duration
                WHERE username = ? AND date = date('now') AND exercise_name = ?
                GROUP BY date;
            """
            cursor.execute(query, (username, exercise_name))
        elif view_type == "weekly":
            # Fetch progress for the past 7 days
            query = """
                SELECT date, SUM(reps), SUM(duration)
                FROM exercise_progress_with_duration
                WHERE username = ? AND date >= date('now', '-7 days') AND exercise_name = ?
                GROUP BY date;
            """
            cursor.execute(query, (username, exercise_name))
        elif view_type == "monthly":
            # Fetch progress for the past 30 days
            query = """
                SELECT date, SUM(reps), SUM(duration)
                FROM exercise_progress_with_duration
                WHERE username = ? AND date >= date('now', '-30 days') AND exercise_name = ?
                GROUP BY date;
            """
            cursor.execute(query, (username, exercise_name))

        rows = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching progress: {e}")
        return jsonify({'message': 'Failed to fetch progress'}), 500
    finally:
        conn.close()

    # Prepare JSON response
    return jsonify([
        {'date': row[0], 'reps': row[1], 'duration': row[2]} for row in rows
    ])


@app.route('/api/get_streak', methods=['GET'])
def get_streak():
    username = session.get('username')
    if not username:
        return jsonify({'message': 'User not logged in'}), 401

    conn = sqlite3.connect('exercise_progress_with_duration.db')
    cursor = conn.cursor()
    
    # Query all distinct workout dates for the user, sorted in descending order
    cursor.execute("""
        SELECT DISTINCT date FROM exercise_progress_with_duration
        WHERE username = ?
        ORDER BY date DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()

    # Calculate streak
    streak = 0
    previous_date = None
    today = date.today()

    for row in rows:
        current_date = date.fromisoformat(row[0])
        if previous_date is None:  # First date
            if current_date == today or current_date == (today - timedelta(days=1)):
                streak += 1
            else:
                break
        else:
            if (previous_date - current_date).days == 1:
                streak += 1
            else:
                break
        previous_date = current_date

    return jsonify({'streak': streak})


if __name__ == "__main__":
    app.run(debug=True)
