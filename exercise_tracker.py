import cv2
import mediapipe as mp
import numpy as np
import pyttsx3

# Initialize MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

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

def change_exercise(exercise):
    """Change the current exercise"""
    global current_exercise
    if exercise in exercises:
        current_exercise = exercise
        exercises[current_exercise]['stage'] = None
        return {'success': True}
    else:
        return {'success': False}

def set_target_reps(reps):
    """Set the target number of repetitions"""
    global target_reps, target_achieved
    
    target_reps = reps
    target_achieved = False
    return {'target_reps': target_reps}

def start_exercise():
    """Start the exercise tracking"""
    global exercise_started, exercises, target_achieved, cap
    
    exercise_started = True
    target_achieved = False
    
    for exercise in exercises.values():
        exercise['counter'] = 0  # Reset counters on start
    
    # Reinitialize video capture
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
    
    return {'success': True}

def stop_exercise():
    """Stop the exercise tracking"""
    global exercise_started, cap,target_achieved
    
    exercise_started = False
    target_achieved = False   # Ensure this is reset

    # Release video capture
    if cap is not None and cap.isOpened():
        cap.release()
        cap = None
    
    return {'success': True}

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
                    elif current_exercise == 'bicep_curl_right':
                        process_bicep_curl(landmarks, side='RIGHT')
                    elif current_exercise == 'overhead_press_left':
                        process_overhead_press(landmarks, side='LEFT')
                    elif current_exercise == 'overhead_press_right':
                        process_overhead_press(landmarks, side='RIGHT')
                    elif current_exercise == 'lateral_raise_left':
                        process_lateral_raise(landmarks, side='LEFT')
                    elif current_exercise == 'lateral_raise_right':
                        process_lateral_raise(landmarks, side='RIGHT')
                    elif current_exercise == 'front_raise_left':
                        process_front_raise(landmarks, side='LEFT')
                    elif current_exercise == 'front_raise_right':
                        process_front_raise(landmarks, side='RIGHT')
                    elif current_exercise == 'single_arm_dumbbell_left':
                        process_single_arm_dumbbell(landmarks, side='LEFT')
                    elif current_exercise == 'single_arm_dumbbell_right':
                        process_single_arm_dumbbell(landmarks, side='RIGHT')

                    # Announce when the target is achieved
                    if target_achieved:
                        announce_target_achieved()
                        exercise_started = False   # Stop exercise tracking
                        target_achieved = False  # Prevent repeated announcements 

                except Exception as e:
                    print(f"Error processing frame: {e}")
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
                cv2.putText(image, exercises[current_exercise]['stage'] or "", 
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
    # Release video capture after the loop ends
    if cap is not None and cap.isOpened():
        cap.release()
    
# New exercise processing functions can be defined below
def process_bicep_curl(landmarks, side):
    """Logic for bicep curls (left/right)"""
    global exercises, target_reps, target_achieved
    exercise_key = f'bicep_curl_{side.lower()}'
    if current_exercise != exercise_key:
        return
    
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

        if exercises[f'bicep_curl_{side.lower()}']['counter'] >= target_reps > 0:
            if not target_achieved:  # Only trigger when target_achieved is False
                target_achieved = True
                announce_target_achieved()

def process_overhead_press(landmarks, side):
    """Logic for overhead presses (left/right)"""
    global exercises, target_reps, target_achieved

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

    angle = calculate_angle(elbow, shoulder, wrist)

    # Overhead press logic
    if angle < 70:
        exercises[f'overhead_press_{side.lower()}']['stage'] = "down"
    if angle > 160 and exercises[f'overhead_press_{side.lower()}']['stage'] == "down":
        exercises[f'overhead_press_{side.lower()}']['stage'] = "up"
        exercises[f'overhead_press_{side.lower()}']['counter'] += 1

        if exercises[f'overhead_press_{side.lower()}']['counter'] >= target_reps > 0:
            if not target_achieved:  # Only trigger when target_achieved is False
                target_achieved = True
                announce_target_achieved()

def process_lateral_raise(landmarks, side):
    """Logic for lateral raises (left/right)"""
    global exercises, target_reps, target_achieved

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

    # Lateral raise logic
    if angle < 30:
        exercises[f'lateral_raise_{side.lower()}']['stage'] = "down"
    if angle > 90 and exercises[f'lateral_raise_{side.lower()}']['stage'] == "down":
        exercises[f'lateral_raise_{side.lower()}']['stage'] = "up"
        exercises[f'lateral_raise_{side.lower()}']['counter'] += 1

        if exercises[f'lateral_raise_{side.lower()}']['counter'] >= target_reps > 0:
            if not target_achieved:  # Only trigger when target_achieved is False
                target_achieved = True
                announce_target_achieved()

def process_front_raise(landmarks, side):
    """Logic for front raises (left/right)"""
    global exercises, target_reps, target_achieved

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

    # Front raise logic
    if angle < 30:
        exercises[f'front_raise_{side.lower()}']['stage'] = "down"
    if angle > 90 and exercises[f'front_raise_{side.lower()}']['stage'] == "down":
        exercises[f'front_raise_{side.lower()}']['stage'] = "up"
        exercises[f'front_raise_{side.lower()}']['counter'] += 1

        if exercises[f'front_raise_{side.lower()}']['counter'] >= target_reps > 0:
            if not target_achieved:  # Only trigger when target_achieved is False
                target_achieved = True
                announce_target_achieved()

def process_single_arm_dumbbell(landmarks, side):
    """Logic for single-arm dumbbell exercise (left/right)"""
    global exercises, target_reps, target_achieved

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

        print(f"{side} Arm Dumbbell Count: {exercises[f'single_arm_dumbbell_{side.lower()}']['counter']}")

        if exercises[f'single_arm_dumbbell_{side.lower()}']['counter'] >= target_reps > 0:
            if not target_achieved:  # Only trigger when target_achieved is False
                target_achieved = True
                announce_target_achieved()
