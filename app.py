from flask import Flask, request, jsonify, session, redirect, url_for,Response
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import sqlite3

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp.solutions.pose

# Global variables for exercise state management
exercise_started = False
target_reps = 0
target_achieved = False
cap = None
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

# Curl counter variables
exercises = {
    'bicep_curl': {'counter': 0, 'stage': None},
    'single_arm_dumbbell': {'counter': 0, 'stage': None}
}
current_exercise = 'bicep_curl'

# Function to calculate angle
def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

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
        for exercise in exercises.values():
            exercise['counter'] = 0  # Reset counters on login
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

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

# API endpoint for getting exercise data
@app.route('/api/exercises', methods=['GET'])
def get_exercises():
    return jsonify(exercises)

# API endpoint for changing the current exercise
@app.route('/api/change_exercise', methods=['POST'])
def api_change_exercise():
    global current_exercise
    data = request.get_json()
    exercise = data.get('exercise')
    if exercise in exercises:
        current_exercise = exercise
        return jsonify({'message': 'Exercise changed successfully'})
    else:
        return jsonify({'message': 'Invalid exercise'}), 400
# API endpoint for setting the target
@app.route('/api/set_target', methods=['POST'])
def set_target():
    global target_reps, target_achieved
    data = request.get_json()
    target_reps = data.get('target_reps', 0)
    target_achieved = False
    return jsonify({'message': 'Target set successfully', 'target_reps': target_reps})

# API endpoint for starting the exercise
@app.route('/api/start', methods=['POST'])
def start_exercise():
    global exercise_started, exercises,target_achieved,cap
    exercise_started = True
    target_achieved = False
    for exercise in exercises.values():
        exercise['counter'] = 0  # Reset counters on start
    # Reinitialize video capture
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
    return jsonify({'message': 'Exercise started'})

# API endpoint for stopping the exercise
@app.route('/api/stop', methods=['POST'])
def stop_exercise():
    global exercise_started,cap
    exercise_started = False
     # Release video capture
    if cap is not None and cap.isOpened():
        cap.release()
        cap = None
    return jsonify({'message': 'Exercise stopped'})
# Video Capture
cap = cv2.VideoCapture(0)

def generate_frames():
    global exercises, current_exercise, target_reps, target_achieved, exercise_started
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while True:
            success, frame = cap.read()
            if not success or not exercise_started:
                break
            else:
                # Recolor image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                results = pose.process(image)

                # Recolor back to BGR
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Extract landmarks
                try:
                    landmarks = results.pose_landmarks.landmark

                    if current_exercise == 'bicep_curl':
                        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                        angle = calculate_angle(shoulder, elbow, wrist)

                        # Curl counter logic
                        if angle > 160:
                            exercises['bicep_curl']['stage'] = "down"
                        if angle < 30 and exercises['bicep_curl']['stage'] == 'down':
                            exercises['bicep_curl']['stage'] = "up"
                            exercises['bicep_curl']['counter'] += 1
                            print(exercises['bicep_curl']['counter'])

                            if exercises['bicep_curl']['counter'] >= target_reps:
                                target_achieved = True

                    elif current_exercise == 'single_arm_dumbbell':
                        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                        angle = calculate_angle(shoulder, elbow, wrist)

                        # Single arm dumbbell counter logic
                        if angle > 160:
                            exercises['single_arm_dumbbell']['stage'] = "down"
                        if angle < 30 and exercises['single_arm_dumbbell']['stage'] == 'down':
                            exercises['single_arm_dumbbell']['stage'] = "up"
                            exercises['single_arm_dumbbell']['counter'] += 1
                            print(exercises['single_arm_dumbbell']['counter'])

                            if exercises['single_arm_dumbbell']['counter'] >= target_reps:
                                target_achieved = True

                except:
                    pass

                # Render curl counter
                cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)
                
                # Rep data
                cv2.putText(image, 'REPS', (15, 12), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, str(exercises[current_exercise]['counter']), 
                            (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

                # Stage data
                cv2.putText(image, 'STAGE', (65, 12), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, exercises[current_exercise]['stage'], 
                            (60, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

                if target_achieved:
                    cv2.putText(image, 'Target Achieved!', (15, 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

                # Render landmarks
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2), 
                                          mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', image)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/api/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
