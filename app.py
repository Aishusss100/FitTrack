from flask import Flask, request, jsonify, session, redirect, url_for, Response
from flask_cors import CORS
import sqlite3
from datetime import date, timedelta,datetime

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
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP, -- Automatically store the current timestamp
            UNIQUE(username, exercise_name, date) ON CONFLICT REPLACE
        );
    ''')
    conn.commit()
    conn.close()

def init_user_goals_db():
    conn = sqlite3.connect('exercise_progress_with_duration.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each goal
            username TEXT NOT NULL,               -- User the goal belongs to
            exercise_name TEXT NOT NULL,          -- Exercise for the goal (e.g., push-ups)
            target_reps INTEGER DEFAULT 0,        -- Target reps for the goal
            target_duration INTEGER DEFAULT 0,    -- Target duration in seconds
            days_to_complete INTEGER NOT NULL,    -- Time frame to complete the goal in days
            created_at DATE NOT NULL,             -- Creation date for the goal
            is_achieved BOOLEAN DEFAULT 0,        -- Indicates if the goal is achieved (0 = No, 1 = Yes)
            FOREIGN KEY(username) REFERENCES users(username) -- Link to users table
        );
    ''')
    conn.commit()
    conn.close()
    print("Table user_goals created successfully!")


# Initialize both databases
init_user_db()
init_progress_db()
init_user_goals_db()
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
    print("Session data:", session)  # Log session data
    username = session.get('username', None)
    if not username:
        print("User not logged in")  # Log if user is not logged in
        return jsonify({'message': 'User not logged in'}), 401
    print("Username:", username)  # Log the retrieved username
    return jsonify({'username': username})


def update_progress_internal(data):
    username = session.get('username')
    if not username:
        return {'message': 'User not logged in', 'success': False}

    exercise_name = data.get('exercise_name')
    reps = data.get('reps', 0)
    duration = data.get('duration', 0)  # Duration in seconds
    today = str(date.today())
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current timestamp

    conn = sqlite3.connect('exercise_progress_with_duration.db')  # Use the new table
    cursor = conn.cursor()
    try:
        # Insert or update the progress while updating the timestamp
        cursor.execute("""
            INSERT INTO exercise_progress_with_duration (username, exercise_name, date, reps, duration, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(username, exercise_name, date)
            DO UPDATE SET 
                reps = reps + ?, 
                duration = duration + ?, 
                timestamp = ?;
        """, (username, exercise_name, today, reps, duration, current_timestamp, reps, duration, current_timestamp))
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

# Add this endpoint to your app.py file

@app.route('/api/get_total_calories', methods=['GET'])
def get_total_calories():
    username = session.get('username')
    if not username:
        return jsonify({'message': 'User not logged in'}), 401

    view_type = request.args.get('view_type', 'daily')  # Default to daily
    
    # Connect to the SQLite database
    conn = sqlite3.connect('exercise_progress_with_duration.db')
    cursor = conn.cursor()

    try:
        # Query based on view type
        if view_type == "daily":
            # Fetch total progress for today across all exercises
            query = """
                SELECT SUM(reps) AS total_reps, SUM(duration) AS total_duration
                FROM exercise_progress_with_duration
                WHERE username = ? AND DATE(date, 'localtime') = DATE('now', 'localtime');
            """
            cursor.execute(query, (username,))
        elif view_type == "weekly":
            # Fetch total progress for the past 7 days across all exercises
            query = """
                SELECT SUM(reps) AS total_reps, SUM(duration) AS total_duration
                FROM exercise_progress_with_duration
                WHERE username = ? AND DATE(date, 'localtime') >= DATE('now', '-7 days', 'localtime');
            """
            cursor.execute(query, (username,))
        elif view_type == "monthly":
            # Fetch total progress for the past 30 days across all exercises
            query = """
                SELECT SUM(reps) AS total_reps, SUM(duration) AS total_duration
                FROM exercise_progress_with_duration
                WHERE username = ? AND DATE(date, 'localtime') >= DATE('now', '-30 days', 'localtime');
            """
            cursor.execute(query, (username,))

        # Fetch the totals
        result = cursor.fetchone()
        total_reps = result[0] or 0
        total_duration = result[1] or 0
        
        # Calculate calories burned using the same formula as the frontend
        calories_burned = total_reps * 0.1 + (total_duration / 60) * 0.15
        
    except Exception as e:
        print(f"Error calculating calories: {e}")
        return jsonify({'message': 'Failed to calculate calories'}), 500
    finally:
        conn.close()

    # Return calories data as JSON response
    return jsonify({
        'calories_burned': round(calories_burned, 2),
        'total_reps': total_reps,
        'total_duration': total_duration
    })

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
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current timestamp

    conn = sqlite3.connect('exercise_progress_with_duration.db')  # Use the new table
    cursor = conn.cursor()
    try:
        # Insert or update the progress while updating the timestamp
        cursor.execute("""
            INSERT INTO exercise_progress_with_duration (username, exercise_name, date, reps, duration, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(username, exercise_name, date)
            DO UPDATE SET 
                reps = reps + ?, 
                duration = duration + ?, 
                timestamp = ?;
        """, (username, exercise_name, today, reps, duration, current_timestamp, reps, duration, current_timestamp))
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


@app.route('/api/get_progress', methods=['GET'])
def get_progress():
    username = session.get('username')
    if not username:
        return jsonify({'message': 'User not logged in'}), 401

    view_type = request.args.get('view_type')  # Accept "daily", "weekly", "monthly"
    exercise_name = request.args.get('exercise_name')

    # Connect to the SQLite database
    conn = sqlite3.connect('exercise_progress_with_duration.db')
    cursor = conn.cursor()

    try:
        # Query based on view type
        if view_type == "daily":
            # Fetch progress for today based on local time
            query = """
                SELECT DATE(date, 'localtime') AS date, SUM(reps) AS total_reps, SUM(duration) AS total_duration
                FROM exercise_progress_with_duration
                WHERE username = ? AND DATE(date, 'localtime') = DATE('now', 'localtime') AND exercise_name = ?
                GROUP BY DATE(date, 'localtime');
            """
            cursor.execute(query, (username, exercise_name))
        elif view_type == "weekly":
            # Fetch progress for the past 7 days (including today)
            query = """
                SELECT DATE(date, 'localtime') AS date, SUM(reps) AS total_reps, SUM(duration) AS total_duration
                FROM exercise_progress_with_duration
                WHERE username = ? AND DATE(date, 'localtime') >= DATE('now', '-7 days', 'localtime') AND exercise_name = ?
                GROUP BY DATE(date, 'localtime');
            """
            cursor.execute(query, (username, exercise_name))
        elif view_type == "monthly":
            # Fetch progress for the past 30 days (including today)
            query = """
                SELECT DATE(date, 'localtime') AS date, SUM(reps) AS total_reps, SUM(duration) AS total_duration
                FROM exercise_progress_with_duration
                WHERE username = ? AND DATE(date, 'localtime') >= DATE('now', '-30 days', 'localtime') AND exercise_name = ?
                GROUP BY DATE(date, 'localtime');
            """
            cursor.execute(query, (username, exercise_name))

        # Fetch and format the rows from the database
        rows = cursor.fetchall()
        progress_data = [
            {'date': row[0], 'reps': row[1], 'duration': row[2]} for row in rows
        ]
    except Exception as e:
        print(f"Error fetching progress: {e}")
        return jsonify({'message': 'Failed to fetch progress'}), 500
    finally:
        conn.close()

    # Return progress data as JSON response
    return jsonify(progress_data)



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


@app.route('/api/create_goal', methods=['POST'])
def create_goal():
    # Check if user is logged in
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 401
    
    data = request.get_json()
    
    # Enhanced validation
    exercise_name = data.get('exercise_name', '').strip()
    
    # Convert to integers and handle potential conversion errors
    try:
        target_reps = int(data.get('target_reps', ''))
        target_duration = int(data.get('target_duration', ''))
        days_to_complete = int(data.get('days_to_complete', ''))
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid numeric inputs'}), 400
    
    # Comprehensive input validation
    if not exercise_name:
        return jsonify({'message': 'Exercise name is required'}), 400
    
    if target_reps <= 0:
        return jsonify({'message': 'Target reps must be greater than 0'}), 400
    
    if target_duration <= 0:
        return jsonify({'message': 'Target duration must be greater than 0'}), 400
    
    if days_to_complete <= 0:
        return jsonify({'message': 'Days to complete must be greater than 0'}), 400
    
    username = session['username']
    created_at = date.today()
    
    conn = sqlite3.connect('exercise_progress_with_duration.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO user_goals (username, exercise_name, target_reps, target_duration, days_to_complete, created_at, is_achieved)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', (username, exercise_name, target_reps, target_duration, days_to_complete, created_at))
        conn.commit()
        
        # Get the ID of the newly created goal
        new_goal_id = c.lastrowid
        
        return jsonify({
            'message': 'Goal created successfully!',
            'goal': {
                'id': new_goal_id,
                'exercise_name': exercise_name,
                'target_reps': target_reps,
                'target_duration': target_duration,
                'days_to_complete': days_to_complete,
                'created_at': str(created_at),
                'is_achieved': False
            }
        })
    except Exception as e:
        print(f"Error creating goal: {e}")
        return jsonify({'message': 'Failed to create goal'}), 500
    finally:
        conn.close()

        
@app.route('/api/get_goals', methods=['GET'])
def get_goals():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    is_achieved = request.args.get('is_achieved', None)  # Filter by active/achieved goals
    username = session['username']

    conn = sqlite3.connect('exercise_progress_with_duration.db')
    c = conn.cursor()
    try:
        query = '''
            SELECT id, exercise_name, target_reps, target_duration, days_to_complete, created_at, is_achieved
            FROM user_goals
            WHERE username = ?
        '''
        params = [username]
        if is_achieved is not None:
            query += ' AND is_achieved = ?'
            params.append(is_achieved)

        c.execute(query, params)
        goals = c.fetchall()

        result = [
            {
                'id': goal[0],
                'exercise_name': goal[1],
                'target_reps': goal[2],
                'target_duration': goal[3],
                'days_to_complete': goal[4],
                'created_at': goal[5],
                'is_achieved': bool(goal[6]),
            }
            for goal in goals
        ]
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching goals: {e}")
        return jsonify({'message': 'Failed to fetch goals'}), 500
    finally:
        conn.close()

# Delete a goal
@app.route('/api/delete_goal', methods=['DELETE'])
def delete_goal():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    goal_id = request.args.get('id')

    conn = sqlite3.connect('exercise_progress_with_duration.db')
    c = conn.cursor()
    try:
        c.execute('DELETE FROM user_goals WHERE id = ?', (goal_id,))
        conn.commit()
        return jsonify({'message': 'Goal deleted successfully!'})
    except Exception as e:
        print(f"Error deleting goal: {e}")
        return jsonify({'message': 'Failed to delete goal'}), 500
    finally:
        conn.close()

# Update goal status (e.g., when a target is achieved)
@app.route('/api/update_goal_status', methods=['POST'])
def update_goal_status():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    goal_id = request.json.get('id')
    is_achieved = request.json.get('is_achieved', 0)

    conn = sqlite3.connect('exercise_progress_with_duration.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE user_goals SET is_achieved = ? WHERE id = ?', (is_achieved, goal_id))
        conn.commit()
        return jsonify({'message': 'Goal status updated successfully!'})
    except Exception as e:
        print(f"Error updating goal status: {e}")
        return jsonify({'message': 'Failed to update goal status'}), 500
    finally:
        conn.close()

@app.route('/api/check_goal_progress', methods=['GET'])
def check_goal_progress():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    goal_id = request.args.get('goal_id')
    
    conn = sqlite3.connect('exercise_progress_with_duration.db')
    c = conn.cursor()
    
    try:
        # First, get the goal details
        c.execute('''
            SELECT exercise_name, target_reps, target_duration, days_to_complete, created_at
            FROM user_goals 
            WHERE id = ? AND username = ?
        ''', (goal_id, session['username']))
        goal = c.fetchone()
        
        if not goal:
            return jsonify({'message': 'Goal not found'}), 404
        
        exercise_name, target_reps, target_duration, days_to_complete, created_at = goal
        
        # Calculate the date range for progress
        start_date = date.fromisoformat(created_at)
        end_date = start_date + timedelta(days=days_to_complete)
        today = date.today()
        
        # Fetch progress for this specific exercise within the goal's timeframe
        c.execute('''
            SELECT SUM(reps) as total_reps, SUM(duration) as total_duration
            FROM exercise_progress_with_duration
            WHERE username = ? 
            AND exercise_name = ? 
            AND date BETWEEN ? AND ?
        ''', (session['username'], exercise_name, start_date, end_date))
        
        progress = c.fetchone()
        total_reps = progress[0] or 0
        total_duration = progress[1] or 0
        
        # Calculate progress percentages
        reps_progress = min((total_reps / target_reps) * 100, 100) if target_reps > 0 else 0
        duration_progress = min((total_duration / target_duration) * 100, 100) if target_duration > 0 else 0
        
        # Determine if goal is achieved
        is_achieved = reps_progress >= 100 
        
        # If goal is achieved, update the goal status
        if is_achieved:
            c.execute('''
                UPDATE user_goals 
                SET is_achieved = 1 
                WHERE id = ?
            ''', (goal_id,))
            conn.commit()
        
        return jsonify({
            'goal_id': goal_id,
            'exercise_name': exercise_name,
            'target_reps': target_reps,
            'current_reps': total_reps,
            'reps_progress': reps_progress,
            'target_duration': target_duration,
            'current_duration': total_duration,
            'duration_progress': duration_progress,
            'is_achieved': is_achieved,
            'start_date': created_at,
            'end_date': str(end_date),
            'days_to_complete': days_to_complete
        })
    
    except Exception as e:
        print(f"Error checking goal progress: {e}")
        return jsonify({'message': 'Failed to check goal progress'}), 500
    finally:
        conn.close()

@app.route('/api/get_achieved_goals', methods=['GET'])
def get_achieved_goals():
    if 'username' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    username = session['username']

    conn = sqlite3.connect('exercise_progress_with_duration.db')
    c = conn.cursor()
    try:
        query = '''
            SELECT id, exercise_name, target_reps, target_duration, days_to_complete, created_at
            FROM user_goals
            WHERE username = ? AND is_achieved = 1
        '''
        c.execute(query, (username,))
        goals = c.fetchall()

        result = [
            {
                'id': goal[0],
                'exercise_name': goal[1],
                'target_reps': goal[2],
                'target_duration': goal[3],
                'days_to_complete': goal[4],
                'created_at': goal[5],
            }
            for goal in goals
        ]
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching achieved goals: {e}")
        return jsonify({'message': 'Failed to fetch achieved goals'}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
