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


# Initialize MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

tts_lock = threading.Lock()
is_speaking = False
temp_dir = tempfile.gettempdir() 

tts_engine = pyttsx3.init()

def announce_target_achieved():
    """Announce that the target is achieved."""
    tts_engine.say("Target achieved!")
    tts_engine.runAndWait()

# Global variables for exercise state management
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
# Define a global username variable
username = "default_user"  # This can be set via a function later if needed


def init_exercise_tracker():
    """Initialize or reset the exercise tracker state"""
    global exercises, current_exercise, exercise_started, target_reps, target_achieved
    
    for exercise in exercises.values():
        exercise['counter'] = 0
        exercise['stage'] = None
    
    exercise_started = False
    target_reps = 0
    target_achieved = False

def get_exercise_data():
    """Return the current exercise data"""
    return exercises

def change_exercise(exercise_name):
    """Change the current exercise."""
    global current_exercise

    # Validate if the exercise exists
    if exercise_name not in exercises:
        print(f"Invalid exercise: {exercise_name}")
        return {'success': False, 'message': 'Exercise not found'}

    current_exercise = exercise_name  # Set the current exercise
    print(f"Current exercise changed to: {current_exercise}")

    # Reset the stage for the selected exercise
    exercises[current_exercise]['stage'] = None
    return {'success': True, 'message': f'Exercise changed to {current_exercise}'}

def set_target_reps(reps):
    """Set the target number of repetitions"""
    global target_reps, target_achieved
    
    target_reps = reps
    target_achieved = False
    return {'target_reps': target_reps}

import requests
# Fetch username dynamically from the backend
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
    

# Define the backend API endpoint for updating progress
API_URL = "http://localhost:5000/api/update_progress"

def update_progress_api(exercise_name, reps):
    # Fetch the username dynamically
    username = fetch_username()
    if not username:
        print("No user is logged in. Cannot update progress.")
        return

    payload = {
        "username": username,
        "exercise_name": exercise_name,
        "reps": reps
    }
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"Progress updated: {exercise_name} - {reps} reps")
        else:
            print(f"Failed to update progress: {response.text}")
    except Exception as e:
        print(f"Error updating progress: {e}")


def start_exercise(exercise_name):
    """Start the exercise tracking and set the current exercise."""
    global exercise_started, target_achieved, current_exercise, exercises, cap  # Include cap here

    exercise_started = True
    target_achieved = False
    current_exercise = exercise_name  # Set the current exercise
    print(f"Current exercise set to: {current_exercise}")

    # Reset counters for all exercises
    for exercise in exercises.values():
        exercise['counter'] = 0
        exercise['stage'] = None

    # Ensure proper initialization of video capture
    if cap is None:
        cap = cv2.VideoCapture(0)  # Initialize cap
    elif not cap.isOpened():
        cap.open(0)  # Open cap if it is closed

    return {'success': True, 'message': f'{current_exercise} started'}

def stop_exercise():
    """Stop the exercise tracking"""
    global exercise_started, cap, target_achieved, current_exercise, exercises
    
    exercise_started = False
    target_achieved = False
    
    # Get the current exercise data before stopping
    exercise_data = {
        'exercise_name': current_exercise,
        'reps': exercises[current_exercise]['counter']
    }
    
    # Release video capture
    if cap is not None and cap.isOpened():
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

def announce_feedback(message):
    """
    Announce feedback asynchronously using gTTS and playsound.
    """
    global is_speaking
    
    with tts_lock:
        if not is_speaking:
            is_speaking = True
            threading.Thread(target=_announce, args=(message,), daemon=True).start()
        else:
            print(f"[Queued Feedback]: {message}")


# def announce_target_achieved():
#     print("Target Achieved Announcement Triggered")
#     announce_feedback("Target achieved!")

def _announce(message):
    """Thread function for TTS handling."""
    global is_speaking
    
    try:
        # Create a temporary file for TTS audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        
        # Generate the TTS audio file
        tts = gTTS(text=message, lang='en', slow=False)
        tts.save(temp_file)
        
        # Play the audio file
        if os.path.exists(temp_file):
            playsound(temp_file)
        else:
            print(f"Error: File {temp_file} does not exist.")
        
        # Clean up temporary file
        try:
            os.remove(temp_file)
            print(f"Temporary file {temp_file} deleted successfully.")
        except FileNotFoundError:
            print(f"File {temp_file} not found for cleanup.")
        except Exception as e:
            print(f"Error deleting temporary file: {e}")
    
    except Exception as e:
        print(f"TTS Error: {e}")
    finally:
        with tts_lock:
            is_speaking = False


import time



def check_posture(landmarks):
    """
    Improved posture check that detects forward bending, sideways leaning using angle measurements, and forward slouching
    using the shoulder-to-hip distance, with adjusted thresholds to reduce false positives.
    """
    # Extract relevant landmarks for posture assessment
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    
    # Add neck approximation (midpoint between shoulders, slightly higher)
    neck_x = (left_shoulder.x + right_shoulder.x) / 2
    neck_y = ((left_shoulder.y + right_shoulder.y) / 2) - 0.03  # Slightly higher than shoulders
    
    # Calculate midpoints for shoulders and hips
    shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
    shoulder_midpoint_y = (left_shoulder.y + right_shoulder.y) / 2
    hip_midpoint_x = (left_hip.x + right_hip.x) / 2
    hip_midpoint_y = (left_hip.y + right_hip.y) / 2
    
    # Define appropriate thresholds
    SHOULDER_THRESHOLD = 0.035
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

    # Debugging outputs
    # print(f"Sideways Vector: {sideways_vector}, Sideways Angle: {sideways_angle:.2f}°, Direction: {leaning_direction}")

    # Check if sideways angle exceeds threshold
    sideways_lean = sideways_angle > SIDEWAYS_ANGLE_THRESHOLD

    # Forward slouching using shoulder-to-hip distance
    shoulder_to_hip_distance = ((shoulder_midpoint_x - hip_midpoint_x)**2 + 
                                (shoulder_midpoint_y - hip_midpoint_y)**2)**0.5
    forward_slouch = shoulder_to_hip_distance < FORWARD_SLOUCH_THRESHOLD

    # Debugging output for forward slouch detection
    # print(f"Shoulder-to-Hip Distance: {shoulder_to_hip_distance:.3f}, Threshold: {FORWARD_SLOUCH_THRESHOLD}")

    # Calculate the standard checks as before
    shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
    uneven_shoulders = shoulder_diff > SHOULDER_THRESHOLD
    hip_diff = abs(left_hip.y - right_hip.y)
    uneven_hips = hip_diff > HIP_THRESHOLD
    torso_alignment_issue = abs(shoulder_midpoint_y - hip_midpoint_y) < TORSO_THRESHOLD

    # Initialize posture issue message
    posture_issue = None

    # Prioritize bending issues
    if forward_bending:
        posture_issue = "straighten up - you're bending forward"
    elif backward_bending:
        posture_issue = "straighten up - you're leaning backward"
    elif sideways_lean:
        posture_issue = f"straighten your body - detected sideways leaning "
    elif forward_slouch:
        posture_issue = "pull your head back - you're slouching forward (shoulders too close to hips)"
    elif uneven_shoulders:
        posture_issue = "level your shoulders"
    elif uneven_hips:
        posture_issue = "align your hips"
    elif torso_alignment_issue:
        posture_issue = "elongate your spine - you're compressing your torso"

    # Initialize last issue tracking if not already done
    if not hasattr(check_posture, 'last_issue'):
        check_posture.last_issue = None
    if not hasattr(check_posture, 'last_notification_time'):
        check_posture.last_notification_time = 0
    
    current_time = time.time()
    min_notification_interval = 1.0  # Minimum seconds between notifications

    # Debug data for detection - useful for troubleshooting
    debug_info = f"Direction: {leaning_direction}, Forward: {forward_bending}, Backward: {backward_bending}, Sideways Angle: {sideways_angle:.1f}°"
    # print(debug_info)
    
    # Check if we should announce now (new issue or enough time passed)
    if (posture_issue != check_posture.last_issue or 
            (posture_issue and current_time - check_posture.last_notification_time > min_notification_interval)):
        
        check_posture.last_issue = posture_issue
        check_posture.last_notification_time = current_time
        
        if posture_issue:
            feedback_message = f"Please {posture_issue}"
            announce_feedback(feedback_message)
            return f"Posture Correction: {posture_issue}"
        else:
            announce_feedback("Good posture detected")
            return "Posture Feedback: Good posture!"
    
    # Return current status without announcing again
    if posture_issue:
        return f"Posture Feedback: Needs correction ({posture_issue})"
    else:
        return "Posture Feedback: Good posture!"



def generate_video_frames():
    """Generate video frames with pose detection and exercise tracking"""
    global exercises, current_exercise, target_reps, target_achieved, exercise_started, cap
    
    # Initialize video capture if not already done
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
    
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

                    elif current_exercise == 'bicep_curl_right':
                        process_bicep_curl(landmarks, side='RIGHT')
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

                    # Announce when the target is achieved
                    if target_achieved:
                    # Display achievement on screen
                        cv2.putText(image, 'Target Achieved!', (15, 170), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    # Only announce once and then stop tracking
                        if exercise_started:
                            announce_target_achieved()
                            exercise_started = False  # Stop future iterations
                            target_achieved = False
                            # Call stop_exercise if it exists (wrap in try/except in case it doesn't)
                            stop_result = stop_exercise()

                except Exception as e:
                    print(f"Error processing frame: {e}")
                    pass

                # Render curl counter
                cv2.rectangle(image, (0, 0), (255, 170), (245, 117, 245), 0)

                # Rep data
                cv2.putText(image, 'REPS', (15, 32), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 0), 1, cv2.LINE_AA)  # Change to black
                cv2.putText(image, str(exercises[current_exercise]['counter']), 
                            (10, 120), 
                            cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)

                # Stage data
                cv2.putText(image, 'STAGE', (105, 32), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 0), 1, cv2.LINE_AA)  # Change to black
                cv2.putText(image, exercises[current_exercise]['stage'] or "", 
                            (90, 120), 
                            cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)

                # if target_achieved:
                #     cv2.putText(image, 'Target Achieved!', (15, 80), 
                #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

                # Render landmarks
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                         mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2), 
                                         mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', image)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # Release video capture after the loop ends
    if cap is not None and cap.isOpened():
        cap.release()
    
# New exercise processing functions can be defined below
def process_bicep_curl(landmarks, side):
    """Logic for bicep curls (left/right)"""
    # Check posture
    posture_feedback = check_posture(landmarks)
    print(posture_feedback) 

    global exercises, target_reps, target_achieved, username
    exercise_key = f'bicep_curl_{side.lower()}'
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

    # Curl logic
    if angle > 160:
        exercises[f'bicep_curl_{side.lower()}']['stage'] = "down"
    if angle < 30 and exercises[f'bicep_curl_{side.lower()}']['stage'] == "down":
        exercises[f'bicep_curl_{side.lower()}']['stage'] = "up"
        exercises[f'bicep_curl_{side.lower()}']['counter'] += 1

        # Send progress update to the backend
        #update_progress_api(exercise_key, 1)

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
    Simplified lateral raise counter based on wrist horizontal movement
    
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
        wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    else:  # RIGHT
        shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    
    # Calculate horizontal displacement of wrist from shoulder
    horizontal_displacement = abs(wrist.x - shoulder.x)
    
    # Threshold for horizontal movement (adjust as needed)
    HORIZONTAL_MOVEMENT_THRESHOLD = 0.2
    
    # Check if the current stage is down and horizontal movement is significant
    if (horizontal_displacement > HORIZONTAL_MOVEMENT_THRESHOLD and
        exercises[exercise_key]['stage'] == 'down'):
        
        # Mark as up stage and increment counter
        exercises[exercise_key]['stage'] = 'up'
        exercises[exercise_key]['counter'] += 1
        
        # Check if target is achieved
        if exercises[exercise_key]['counter'] >= target_reps > 0:
            if not target_achieved:
                target_achieved = True
                # announce_target_achieved()
    
    # Reset to down stage when horizontal displacement is small
    elif horizontal_displacement < 0.1:
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
    if angle > 160:
        exercises[f'single_arm_dumbbell_{side.lower()}']['stage'] = "down"
    if angle < 30 and exercises[f'single_arm_dumbbell_{side.lower()}']['stage'] == "down":
        exercises[f'single_arm_dumbbell_{side.lower()}']['stage'] = "up"
        exercises[f'single_arm_dumbbell_{side.lower()}']['counter'] += 1

        # Send progress update to the backend
        #update_progress_api(exercise_key, 1)

        print(f"{side} Arm Dumbbell Count: {exercises[f'single_arm_dumbbell_{side.lower()}']['counter']}")

        if exercises[f'single_arm_dumbbell_{side.lower()}']['counter'] >= target_reps > 0:
            if not target_achieved:  # Only trigger when target_achieved is False
                target_achieved = True
                # announce_target_achieved()