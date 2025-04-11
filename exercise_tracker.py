import cv2
import mediapipe as mp
import numpy as np
import requests
from gtts import gTTS
from playsound import playsound
import os
import tempfile
import threading
import math
import pyttsx3
import time
import uuid
import io

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

tts_lock = threading.Lock()
is_speaking = False
# temp_dir = tempfile.gettempdir() 
audio_temp_dir = os.path.join(tempfile.gettempdir(), 'exercise_audio')
os.makedirs(audio_temp_dir, exist_ok=True)

tts_engine = pyttsx3.init()

def announce_target_achieved():
    global latest_event_message
    latest_event_message = "Target achieved!"


exercises = {
    'bicep_curl_left': {'counter': 0, 'stage': None},
    'bicep_curl_right': {'counter': 0, 'stage': None},
    'overhead_press_left': {'counter': 0, 'stage': None},
    'overhead_press_right': {'counter': 0, 'stage': None},
    'lateral_raise_left': {'counter': 0, 'stage': None},
    'lateral_raise_right': {'counter': 0, 'stage': None},
    'front_raise_left': {'counter': 0, 'stage': None},
    'front_raise_right': {'counter': 0, 'stage': None},
    'single_arm_dumbbell_left': {'counter': 0, 'stage': None},
    'single_arm_dumbbell_right': {'counter': 0, 'stage': None}
}
current_exercise = 'bicep_curl_left'
exercise_started = False
target_reps = 0
target_achieved = False
cap = None

username = "default_user" 

last_saved_reps = 0
autosave_thread = None
should_stop_thread = False

def init_exercise_tracker():
    """Initialize or reset the exercise tracker state"""
    global exercises, current_exercise, exercise_started, target_reps, target_achieved
    global last_saved_reps, autosave_thread, should_stop_thread
    
    for exercise in exercises.values():
        exercise['counter'] = 0
        exercise['stage'] = None
    
    exercise_started = False
    target_reps = 0
    target_achieved = False
    last_saved_reps = 0
    should_stop_thread = False
    autosave_thread = None

def get_exercise_data():
    """Return the current exercise data"""
    return exercises

def change_exercise(exercise_name):
    """Change the current exercise."""
    global current_exercise

    
    if exercise_name not in exercises:
        print(f"Invalid exercise: {exercise_name}")
        return {'success': False, 'message': 'Exercise not found'}

    current_exercise = exercise_name 
    print(f"Current exercise changed to: {current_exercise}")

   
    exercises[current_exercise]['stage'] = None
    return {'success': True, 'message': f'Exercise changed to {current_exercise}'}

def set_target_reps(reps):
    """Set the target number of repetitions"""
    global target_reps, target_achieved
    
    target_reps = reps
    target_achieved = False
    return {'target_reps': target_reps}


def fetch_username():
    url = "http://localhost:5000/api/get_username"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('username', None)
        else:
            print(f"Failed to fetch username: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching username: {e}")
        return None
    

API_URL = "http://localhost:5000/api/update_progress"

def update_progress_api(exercise_name, reps, duration=0):
    
    username = fetch_username()
    if not username:
        print("No user is logged in. Cannot update progress.")
        return False

    payload = {
        "exercise_name": exercise_name,
        "reps": reps,
        "duration": duration
    }
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"Progress updated: {exercise_name} - {reps} reps, {duration} seconds")
            return True
        else:
            print(f"Failed to update progress: {response.text}")
            return False
    except Exception as e:
        print(f"Error updating progress: {e}")
        return False

def autosave_progress():
    """Autosave progress every 10 seconds in a reliable manner."""
    global should_stop_thread, last_saved_reps, current_exercise, exercises

    while not should_stop_thread:
        time.sleep(10) 

        if exercise_started and current_exercise in exercises:
            current_reps = exercises[current_exercise]['counter']

            
            if current_reps > last_saved_reps:
                reps_to_save = current_reps - last_saved_reps
                success = update_progress_api(current_exercise, reps_to_save, duration=10)

                if success:
                    print(f"Autosaved {reps_to_save} reps for {current_exercise}")
                    last_saved_reps = current_reps

def start_autosave_thread():
    """Start autosaving in a background thread."""
    global autosave_thread, should_stop_thread

    should_stop_thread = False  

    if autosave_thread is None or not autosave_thread.is_alive():
        autosave_thread = threading.Thread(target=autosave_progress)
        autosave_thread.daemon = True
        autosave_thread.start()

def stop_autosave_thread():
    """Stop the autosave background thread gracefully."""
    global should_stop_thread, autosave_thread

    should_stop_thread = True  

    if autosave_thread and autosave_thread.is_alive():
        autosave_thread.join(2)  

def start_exercise(exercise_name):
    """Start the exercise tracking and set the current exercise."""
    global exercise_started, target_achieved, current_exercise, exercises
    global autosave_thread, should_stop_thread, last_saved_reps

    exercise_started = True
    target_achieved = False
    current_exercise = exercise_name 
    last_saved_reps = 0
    print(f"Current exercise set to: {current_exercise}")

    # Reset all counters and stages
    for exercise in exercises.values():
        exercise['counter'] = 0
        exercise['stage'] = None

    # Start autosave thread
    should_stop_thread = False
    if autosave_thread is None or not autosave_thread.is_alive():
        autosave_thread = threading.Thread(target=autosave_progress)
        autosave_thread.daemon = True
        autosave_thread.start()

    return {'success': True, 'message': f'{current_exercise} started'}
def stop_exercise():
    """Stop the exercise tracking"""
    global exercise_started, target_achieved, current_exercise, exercises
    global autosave_thread, should_stop_thread, last_saved_reps, cap

    exercise_started = False
    target_achieved = False

    should_stop_thread = True
    if autosave_thread and autosave_thread.is_alive():
        autosave_thread.join(2)

    final_reps = 0
    if current_exercise and current_exercise in exercises:
        final_reps = exercises[current_exercise]['counter'] - last_saved_reps

    exercise_data = {
        'exercise_name': current_exercise,
        'reps': final_reps
    }

    # Camera release not needed anymore, but clean up if cap exists
    if 'cap' in globals() and cap is not None and hasattr(cap, "release"):
        if cap.isOpened():
            cap.release()
        cap = None

    return {'success': True, 'exercise_data': exercise_data}


def calculate_angle(a, b, c):
    """Calculate the angle between three points"""
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle


import pygame


pygame.mixer.init()


tts_lock = threading.Lock()
is_speaking = False
temp_files_to_delete = []

def cleanup_worker():
    global temp_files_to_delete
    while True:
        if temp_files_to_delete:
            files_to_try = temp_files_to_delete.copy()
            temp_files_to_delete = []
            
            for file_path in files_to_try:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Successfully deleted: {file_path}")
                except Exception as e:
                    print(f"Could not delete {file_path} yet: {e}")
                    temp_files_to_delete.append(file_path)
        time.sleep(1.0)


cleanup_thread = threading.Thread(target=cleanup_worker)
cleanup_thread.daemon = True
cleanup_thread.start()

def speak_feedback(text):
    """Thread-safe function to speak feedback using gTTS and pygame"""
    global is_speaking, tts_lock, temp_files_to_delete
    
    with tts_lock:
        if is_speaking:
            return False  
        is_speaking = True
    
    def speak_worker():
        global is_speaking, tts_lock, temp_files_to_delete
        try:
            unique_id = str(uuid.uuid4()).replace('-', '')[:8]
            simple_dir = "C:/temp_audio"
            os.makedirs(simple_dir, exist_ok=True)
            temp_file = f"{simple_dir}/tts_{unique_id}.mp3"
            
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file)
            
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            
            time.sleep(0.1)  
            temp_files_to_delete.append(temp_file)

        except Exception as e:
            print(f"TTS Error: {e}")
        finally:
            with tts_lock:
                is_speaking = False
    
    thread = threading.Thread(target=speak_worker)
    thread.daemon = True
    thread.start()
    return True


latest_event_message = None

def announce_feedback(feedback):
    global latest_event_message
    latest_event_message = feedback  # Only store, don’t play

def get_latest_event():
    global latest_event_message
    return latest_event_message

def clear_latest_event():
    global latest_event_message
    latest_event_message = None



def check_posture(landmarks):
    # Extract relevant landmarks for posture assessment
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    
    # Added neck approximation (midpoint between shoulders, slightly higher)
    neck_x = (left_shoulder.x + right_shoulder.x) / 2
    neck_y = ((left_shoulder.y + right_shoulder.y) / 2) - 0.03  
    
    # Calculate midpoints for shoulders and hips
    shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
    shoulder_midpoint_y = (left_shoulder.y + right_shoulder.y) / 2
    hip_midpoint_x = (left_hip.x + right_hip.x) / 2
    hip_midpoint_y = (left_hip.y + right_hip.y) / 2
    
   
    SHOULDER_THRESHOLD = 0.060
    HIP_THRESHOLD = 0.025
    SIDEWAYS_ANGLE_THRESHOLD = 7  # Threshold in degrees for sideways leaning
    FORWARD_SLOUCH_THRESHOLD = 0.15  # Distance threshold for forward slouching
    TORSO_THRESHOLD = 0.15

    # Revised bending detection logic using positional comparisons
    def detect_bending(neck, hip_midpoint):
        """
        Detects forward and backward bending based on positional comparisons.
        """
        # Thresholds for detecting deviations
        VERTICAL_THRESHOLD = 0.03
        DEPTH_THRESHOLD = 0.02

        # Check for forward bending
        is_forward_bending = (neck['y'] > hip_midpoint['y'] + VERTICAL_THRESHOLD) and (neck['z'] < hip_midpoint['z'] - DEPTH_THRESHOLD)

        # Check for backward bending
        is_backward_bending = (neck['y'] < hip_midpoint['y'] - VERTICAL_THRESHOLD) and (neck['z'] > hip_midpoint['z'] + DEPTH_THRESHOLD)

        return is_forward_bending, is_backward_bending

    # Call the new bending detection logic
    forward_bending, backward_bending = detect_bending(
        neck={'x': neck_x, 'y': neck_y, 'z': nose.z}, 
        hip_midpoint={'x': hip_midpoint_x, 'y': hip_midpoint_y, 'z': (left_hip.z + right_hip.z) / 2}
    )

    # Sideways leaning using angle calculation
    sideways_vector = [shoulder_midpoint_x - hip_midpoint_x, shoulder_midpoint_y - hip_midpoint_y]
    vertical_vector = [0, -1]  # Ideal vertical line

    # Calculate angle using dot product
    magnitude_sideways = (sideways_vector[0]**2 + sideways_vector[1]**2)**0.5
    if magnitude_sideways > 0:  # Avoid division by zero
        dot_product = sideways_vector[0] * vertical_vector[0] + sideways_vector[1] * vertical_vector[1]
        cosine_angle = dot_product / magnitude_sideways
        sideways_angle = math.degrees(math.acos(max(-1, min(1, cosine_angle))))
    else:
        sideways_angle = 0

    # Determine leaning direction based on x displacement
    leaning_direction = ""
    if shoulder_midpoint_x > hip_midpoint_x + 0.02:  # Add small offset for sensitivity
        leaning_direction = "right"
    elif shoulder_midpoint_x < hip_midpoint_x - 0.02:
        leaning_direction = "left"

    # Check if sideways angle exceeds threshold
    sideways_lean = sideways_angle > SIDEWAYS_ANGLE_THRESHOLD

    # Forward slouching using shoulder-to-hip distance
    shoulder_to_hip_distance = ((shoulder_midpoint_x - hip_midpoint_x)**2 + 
                                (shoulder_midpoint_y - hip_midpoint_y)**2)**0.5
    forward_slouch = shoulder_to_hip_distance < FORWARD_SLOUCH_THRESHOLD

    # Calculate the standard checks as before
    shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
    uneven_shoulders = shoulder_diff > SHOULDER_THRESHOLD
    hip_diff = abs(left_hip.y - right_hip.y)
    uneven_hips = hip_diff > HIP_THRESHOLD
    torso_alignment_issue = abs(shoulder_midpoint_y - hip_midpoint_y) < TORSO_THRESHOLD

    # Initialize posture issue message
    posture_issue = None

    # Check if current exercise is an overhead press exercise
    is_overhead_press = 'current_exercise' in globals() and current_exercise and ('overhead_press' in current_exercise)

    # Prioritize bending issues
    if forward_bending:
        posture_issue = "straighten up - you're bending forward"
    elif backward_bending:
        posture_issue = "straighten up - you're leaning backward"
    elif sideways_lean:
        posture_issue = f"straighten your body - detected sideways leaning"
    elif forward_slouch:
        posture_issue = "pull your head back - you're slouching forward (shoulders too close to hips)"
    # Skip uneven shoulders check for overhead press exercises
    elif uneven_shoulders and not is_overhead_press:
        posture_issue = "level your shoulders"
    elif uneven_hips:
        posture_issue = "align your hips"
    elif torso_alignment_issue:
        posture_issue = "elongate your spine - you're compressing your torso"

    # Initialize static variables if not already done
    if not hasattr(check_posture, 'last_issue'):
        check_posture.last_issue = None
    if not hasattr(check_posture, 'last_notification_time'):
        check_posture.last_notification_time = 0
    if not hasattr(check_posture, 'issue_confidence'):
        check_posture.issue_confidence = {}
    if not hasattr(check_posture, 'good_posture_notification_time'):
        check_posture.good_posture_notification_time = 0
    if not hasattr(check_posture, 'issue_last_notified'):
        check_posture.issue_last_notified = {}
    if not hasattr(check_posture, 'exercise_started_time'):
        check_posture.exercise_started_time = time.time()
    if not hasattr(check_posture, 'good_posture_streak'):
        check_posture.good_posture_streak = 0
    if not hasattr(check_posture, 'good_posture_confidence'):
        check_posture.good_posture_confidence = 0.0
    
    current_time = time.time()
    
    
    confidence_decay = 0.7  
    confidence_increase = 0.3  
    confidence_threshold = 0.8 
    
   
    for issue in list(check_posture.issue_confidence.keys()):
        if issue != posture_issue:
            check_posture.issue_confidence[issue] = check_posture.issue_confidence[issue] * confidence_decay
            if check_posture.issue_confidence[issue] < 0.1:
                del check_posture.issue_confidence[issue]  # Remove low confidence issues
    
    # Increase confidence for the current issue
    if posture_issue:
        if posture_issue not in check_posture.issue_confidence:
            check_posture.issue_confidence[posture_issue] = 0
        check_posture.issue_confidence[posture_issue] += confidence_increase
        check_posture.issue_confidence[posture_issue] = min(1.0, check_posture.issue_confidence[posture_issue])
    
    # Determine if notification should be sent
    should_notify = False
    
    # Define issue-specific notification intervals (longer for repetitive issues)
    notification_intervals = {
        "level your shoulders": 20.0,  # Longer interval for shoulder level feedback
        "default": 10.0              # Default interval for other issues
    }
    
    if posture_issue and posture_issue in check_posture.issue_confidence:
        confidence = check_posture.issue_confidence[posture_issue]
        
        
        notification_interval = notification_intervals.get(posture_issue, notification_intervals["default"])
        
        
        last_notified = check_posture.issue_last_notified.get(posture_issue, 0)
        time_since_last_notification = current_time - last_notified
        
        
        if confidence >= confidence_threshold and time_since_last_notification > notification_interval:
            should_notify = True
            
            check_posture.issue_last_notified[posture_issue] = current_time
    
   
    good_posture_interval = 45.0  
    good_posture_min_streak = 20  
    warm_up_period = 15.0  
    good_posture_confidence_threshold = 0.85  
    
    current_exercise_time = current_time - check_posture.exercise_started_time
    
    if not posture_issue:
        check_posture.good_posture_streak += 1
        
        check_posture.good_posture_confidence += 0.05
        check_posture.good_posture_confidence = min(1.0, check_posture.good_posture_confidence)
        
       
        if (current_exercise_time > warm_up_period and 
            check_posture.good_posture_streak >= good_posture_min_streak and 
            check_posture.good_posture_confidence >= good_posture_confidence_threshold and
            current_time - check_posture.good_posture_notification_time > good_posture_interval):
            
            
            check_posture.issue_confidence.clear()
            should_notify = True
            check_posture.good_posture_notification_time = current_time
    else:
        
        check_posture.good_posture_streak = 0
        
        check_posture.good_posture_confidence *= 0.5
    
   
    if should_notify:
        check_posture.last_issue = posture_issue
        check_posture.last_notification_time = current_time
        
        if posture_issue:
            feedback_message = f"Please {posture_issue}"
            announce_feedback(feedback_message)
            return f"Posture Correction: {posture_issue}"
        else:
            announce_feedback("Good posture detected")
            return "Posture Feedback: Good posture!"
    

    if posture_issue:
        return f"Posture Feedback: Needs correction ({posture_issue})"
    else:
        return "Posture Feedback: Good posture!"
import io
from flask import send_file
from PIL import Image

def process_incoming_frame(frame_bytes):
    np_arr = np.frombuffer(frame_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    print("Received frame shape:", frame.shape if frame is not None else "None")

    try:
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                # Call exercise logic
                if current_exercise == 'bicep_curl_left':
                    process_bicep_curl(landmarks, side='LEFT')
                    shoulderl = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    elbowl = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    wristl = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    angle = calculate_angle(shoulderl, elbowl, wristl)
                    # Convert landmark coordinates to screen pixels
                    h, w, _ = image.shape
                    elbowl_x, elbowl_y = int(elbowl[0] * w), int(elbowl[1] * h)
                    # Display angle on screen at elbow point
                    cv2.putText(image, str(int(angle)), (elbowl_x, elbowl_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
                elif current_exercise == 'overhead_press_left':
                        process_overhead_press(landmarks, side='LEFT')
                        shoulderl = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        elbowl = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        wristl = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                        angle = calculate_angle(shoulderl, elbowl, wristl)
                        # Convert landmark coordinates to screen pixels
                        h, w, _ = image.shape
                        elbowl_x, elbowl_y = int(elbowl[0] * w), int(elbowl[1] * h)
                        # Display angle on screen at elbow point
                        cv2.putText(image, str(int(angle)), (elbowl_x, elbowl_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

                elif current_exercise == 'overhead_press_right':
                    process_overhead_press(landmarks, side='RIGHT')
                    shoulderr = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    elbowr = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    wristr = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    angle = calculate_angle(shoulderr, elbowr, wristr)
                    # Convert landmark coordinates to screen pixels
                    h, w, _ = image.shape
                    elbowr_x, elbowr_y = int(elbowr[0] * w), int(elbowr[1] * h)
                    # Display angle on screen at elbow point
                    cv2.putText(image, str(int(angle)), (elbowr_x, elbowr_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

                elif current_exercise == 'lateral_raise_left':
                    process_lateral_raise(landmarks, side='LEFT')
                    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    waist = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    angle = calculate_angle(waist ,shoulder, wrist)
                    h, w, _ = image.shape
                    shoulder_x, shoulder_y = int(shoulder[0] * w), int(shoulder[1] * h)
                    # Display angle on screen at shoulder point
                    cv2.putText(image, str(int(angle)), (shoulder_x, shoulder_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

                elif current_exercise == 'lateral_raise_right':
                    process_lateral_raise(landmarks, side='RIGHT')
                    shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    waist = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    angle = calculate_angle(waist ,shoulder, wrist)
                    h, w, _ = image.shape
                    shoulder_x, shoulder_y = int(shoulder[0] * w), int(shoulder[1] * h)
                    # Display angle on screen at shoulder point
                    cv2.putText(image, str(int(angle)), (shoulder_x, shoulder_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

                elif current_exercise == 'front_raise_left':
                    process_front_raise(landmarks, side='LEFT')
                    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    waist = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    angle = calculate_angle(wrist, shoulder, waist)
                    h, w, _ = image.shape
                    shoulder_x, shoulder_y = int(shoulder[0] * w), int(shoulder[1] * h)
                    # Display angle on screen at shoulder point
                    cv2.putText(image, str(int(angle)), (shoulder_x, shoulder_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

                elif current_exercise == 'front_raise_right':
                    process_front_raise(landmarks, side='RIGHT')
                    shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    waist = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    angle = calculate_angle(wrist, shoulder, waist)
                    h, w, _ = image.shape
                    shoulder_x, shoulder_y = int(shoulder[0] * w), int(shoulder[1] * h)
                    # Display angle on screen at shoulder point
                    cv2.putText(image, str(int(angle)), (shoulder_x, shoulder_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

                elif current_exercise == 'single_arm_dumbbell_left':
                    process_single_arm_dumbbell(landmarks, side='LEFT')
                    shoulderl = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    elbowl = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    wristl = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    angle = calculate_angle(shoulderl, elbowl, wristl)
                    # Convert landmark coordinates to screen pixels
                    h, w, _ = image.shape
                    elbowl_x, elbowl_y = int(elbowl[0] * w), int(elbowl[1] * h)
                    # Display angle on screen at elbow point
                    cv2.putText(image, str(int(angle)), (elbowl_x, elbowl_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

                elif current_exercise == 'single_arm_dumbbell_right':
                    process_single_arm_dumbbell(landmarks, side='RIGHT')
                    shoulderr = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    elbowr = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    wristr = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    angle = calculate_angle(shoulderr, elbowr, wristr)
                    # Convert landmark coordinates to screen pixels
                    h, w, _ = image.shape
                    elbowr_x, elbowr_y = int(elbowr[0] * w), int(elbowr[1] * h)
                    # Display angle on screen at elbow point
                    cv2.putText(image, str(int(angle)), (elbowr_x, elbowr_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)


                # Target Achieved message & logic
                global exercise_started, target_achieved
                if target_achieved:
                    if exercise_started:
                        announce_target_achieved()
                        exercise_started = False
                        target_achieved = False
                        stop_exercise()

                # Render REPS and STAGE box
                cv2.rectangle(image, (0, 0), (255, 170), (245, 117, 245), 0)

                # REPS
                cv2.putText(image, 'REPS', (15, 32),
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, str(exercises[current_exercise]['counter']),
                            (10, 120),
                            cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)

                # STAGE
                cv2.putText(image, 'STAGE', (105, 32),
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, exercises[current_exercise]['stage'] or "",
                            (90, 120),
                            cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)

                # Landmarks
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                )

    except Exception as e:
        print("Error processing frame:", e)

    _, buffer = cv2.imencode('.jpg', image)
    return io.BytesIO(buffer)


def process_bicep_curl(landmarks, side):
    """Logic for bicep curls (left/right) with elbow position check"""
    
    posture_feedback = check_posture(landmarks)
    print(posture_feedback)
    
    global exercises, target_reps, target_achieved, username
    exercise_key = f'bicep_curl_{side.lower()}'
    
    if current_exercise != exercise_key:
        return
    
    shoulder, elbow, wrist, hip = None, None, None, None
    
    if side == 'LEFT':
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
               landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
               
    elif side == 'RIGHT':
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
               landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    
    angle = calculate_angle(shoulder, elbow, wrist)
    
    
    horizontal_distance = abs(elbow[0] - hip[0])
    elbow_threshold = 0.15
    good_form = horizontal_distance <= elbow_threshold
    
   
    if not hasattr(process_bicep_curl, 'last_elbow_feedback_time'):
        process_bicep_curl.last_elbow_feedback_time = 0
    
    # Check if elbow is too far from body with cooldown
    current_time = time.time()
    if not good_form and current_time - process_bicep_curl.last_elbow_feedback_time > 1.0:
        feedback_message = f"Keep your {side.lower()} elbow closer to your body"
        announce_feedback(feedback_message)  # Use existing announce_feedback
        process_bicep_curl.last_elbow_feedback_time = current_time
        print(f"Form check: {feedback_message}, distance: {horizontal_distance:.3f}")
    
    
    if angle > 160:
        exercises[f'bicep_curl_{side.lower()}']['stage'] = "down"
    if angle < 30 and exercises[f'bicep_curl_{side.lower()}']['stage'] == "down":
        if good_form:  # Only increment counter if form is good (elbow close to body)
            exercises[f'bicep_curl_{side.lower()}']['stage'] = "up"
            exercises[f'bicep_curl_{side.lower()}']['counter'] += 1
            
            # Send progress update to the backend
            # update_progress_api(exercise_key, 1)
            
            if exercises[f'bicep_curl_{side.lower()}']['counter'] >= target_reps > 0:
                if not target_achieved:  # Only trigger when target_achieved is False
                    target_achieved = True
                    # announce_target_achieved()

def process_overhead_press(landmarks, side):
    # Check posture
    posture_feedback = check_posture(landmarks)
    print(posture_feedback) 

    """Logic for overhead presses (left/right) with vertical check"""
    global exercises, target_reps, target_achieved, username
    exercise_key = f'overhead_press_{side.lower()}'
    if current_exercise != exercise_key:
        return
    shoulder, elbow, wrist = None, None, None
    if side == 'LEFT':
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    elif side == 'RIGHT':
        elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

    angle = calculate_angle(shoulder, elbow, wrist)

    # Verticality check
    is_vertical = abs(wrist[0] - shoulder[0]) < 0.1 and wrist[1] < shoulder[1]  # Example threshold for alignment

    # Overhead press logic
    if 85 < angle < 95:  # Detect 90-degree angle
        exercises[f'overhead_press_{side.lower()}']['stage'] = "down"
    if angle > 165 and exercises[f'overhead_press_{side.lower()}']['stage'] == "down" and is_vertical:  # Check verticality before "up"
        exercises[f'overhead_press_{side.lower()}']['stage'] = "up"
        exercises[f'overhead_press_{side.lower()}']['counter'] += 1

        # Send progress update to the backend
        #update_progress_api(exercise_key, 1)

        if exercises[f'overhead_press_{side.lower()}']['counter'] >= target_reps > 0:
            if not target_achieved:  # Only trigger when target_achieved is False
                target_achieved = True
                # announce_target_achieved()


def process_lateral_raise(landmarks, side):
    """
    Enhanced lateral raise counter based on wrist horizontal movement and shoulder angle
    
    Args:
    landmarks: Mediapipe pose landmarks
    side: 'LEFT' or 'RIGHT' indicating which side to process
    """
    # Check posture
    posture_feedback = check_posture(landmarks)
    print(posture_feedback)
    
    global exercises, target_reps, target_achieved, username, current_exercise
    
    # Define the exercise key based on side
    exercise_key = f'lateral_raise_{side.lower()}'
    
    # Prevent processing if not the current exercise
    if current_exercise != exercise_key:
        return
    
    # Select appropriate landmarks based on side
    if side == 'LEFT':
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    else:  # RIGHT
        shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    
    # Calculate angle at shoulder between hip-shoulder-wrist
    shoulder_angle = calculate_angle(
        [hip.x, hip.y],
        [shoulder.x, shoulder.y],
        [wrist.x, wrist.y]
    )
    
    # Define angle thresholds for lateral raise
    UP_ANGLE_THRESHOLD = 85  # Between 85 and 90 degrees is considered "up"
    DOWN_ANGLE_THRESHOLD = 30  # Less than 30 degrees is considered "down"
    
    # Track horizontal displacement as additional verification
    horizontal_displacement = abs(wrist.x - shoulder.x)
    HORIZONTAL_MOVEMENT_THRESHOLD = 0.2
    
    # Check if arm is raised (up position)
    if (shoulder_angle >= UP_ANGLE_THRESHOLD and 
        horizontal_displacement > HORIZONTAL_MOVEMENT_THRESHOLD and
        exercises[exercise_key]['stage'] == 'down'):
        
        # Mark as up stage and increment counter
        exercises[exercise_key]['stage'] = 'up'
        exercises[exercise_key]['counter'] += 1
        
        # Check if target is achieved
        if exercises[exercise_key]['counter'] >= target_reps > 0:
            if not target_achieved:
                target_achieved = True
                # announce_target_achieved()
    
    # Reset to down stage when angle is small
    elif shoulder_angle < DOWN_ANGLE_THRESHOLD:
        exercises[exercise_key]['stage'] = 'down'

        
def process_front_raise(landmarks, side):
    """Advanced logic for front raises with movement prevention"""
    # Check posture
    posture_feedback = check_posture(landmarks)
    print(posture_feedback) 

    global exercises, target_reps, target_achieved, username, current_exercise
    exercise_key = f'front_raise_{side.lower()}'
    
    # Prevent processing if the current exercise is a lateral raise
    if current_exercise.startswith('lateral_raise'):
        return
    
    # Only process if the current exercise matches this specific front raise
    if current_exercise != exercise_key:
        return

    shoulder, waist, wrist = None, None, None

    # Extract landmarks for the selected side
    if side == 'LEFT':
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        waist = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    elif side == 'RIGHT':
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        waist = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

    # Front raise specific angle calculation
    front_angle = calculate_angle(wrist, shoulder, waist)
    
    # Additional checks to prevent lateral raise-like movements
    # Check arm orientation - for front raise, arm should move more vertically
    arm_orientation_x = abs(wrist[0] - shoulder[0])
    arm_orientation_y = abs(wrist[1] - shoulder[1])
    
    # Ensure arm is moving more vertically than horizontally
    is_front_movement = arm_orientation_y > arm_orientation_x

    # Elbow angle check to ensure proper front raise form
    elbow_angle = calculate_angle(shoulder, elbow, wrist)

    # Front raise logic with additional prevention
    if is_front_movement and front_angle < 20 and 130 < elbow_angle < 180:
        exercises[f'front_raise_{side.lower()}']['stage'] = "down"
    
    if (is_front_movement and 
        front_angle > 70 and 
        exercises[f'front_raise_{side.lower()}']['stage'] == "down" and
        130 < elbow_angle < 180):
        exercises[f'front_raise_{side.lower()}']['stage'] = "up"
        exercises[f'front_raise_{side.lower()}']['counter'] += 1

        if exercises[f'front_raise_{side.lower()}']['counter'] >= target_reps > 0:
            if not target_achieved:
                target_achieved = True
                # announce_target_achieved()

                
def process_single_arm_dumbbell(landmarks, side):
    """Logic for single-arm dumbbell exercise (left/right)"""
    
    
    global exercises, target_reps, target_achieved, username
    exercise_key = f'single_arm_dumbbell_{side.lower()}'
    if current_exercise != exercise_key:
        return
    shoulder, elbow, wrist = None, None, None
    if side == 'LEFT':
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    elif side == 'RIGHT':
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

    angle = calculate_angle(shoulder, elbow, wrist)

    # Dumbbell logic
    if angle > 150:
        exercises[f'single_arm_dumbbell_{side.lower()}']['stage'] = "down"
    if angle < 40 and exercises[f'single_arm_dumbbell_{side.lower()}']['stage'] == "down":
        exercises[f'single_arm_dumbbell_{side.lower()}']['stage'] = "up"
        exercises[f'single_arm_dumbbell_{side.lower()}']['counter'] += 1

        # Send progress update to the backend
        #update_progress_api(exercise_key, 1)

        print(f"{side} Arm Dumbbell Count: {exercises[f'single_arm_dumbbell_{side.lower()}']['counter']}")

        if exercises[f'single_arm_dumbbell_{side.lower()}']['counter'] >= target_reps > 0:
            if not target_achieved:  # Only trigger when target_achieved is False
                target_achieved = True
                # announce_target_achieved()