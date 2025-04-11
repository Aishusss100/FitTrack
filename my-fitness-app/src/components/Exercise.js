import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import "./Exercise.css";
import { useRef } from "react"; // add at top if not already

// Import exercise GIFs
import bicepCurlRightGif from "../assets/One-Arm-Biceps-Curl-right.gif";
import bicepCurlLeftGif from "../assets/One-Arm-Biceps-Curl-left.gif";
import lateralRaiseRightGif from "../assets/lateral raise right.gif";
import lateralRaiseLeftGif from "../assets/lateral raise left.gif";
import frontRaiseRightGif from "../assets/how-to-do-dumbbell-front-raise.gif";
import overheadPressRightGif from "../assets/overhead press right.gif";
import singleArmDumbbellGif from "../assets/single arm dumbell.gif"

const Exercise = () => {
    const { exercise } = useParams();
    const COLORS = {
        DEFAULT: "default",
        TARGET_SET: "target-set",
        TRACKING: "tracking"
    };

    const [targetReps, setTargetReps] = useState("");
    const [tracking, setTracking] = useState(false);
    const [containerState, setContainerState] = useState(COLORS.DEFAULT);
    const [errorMessage, setErrorMessage] = useState("");
    const [elapsedTime, setElapsedTime] = useState(0);
    const [timerId, setTimerId] = useState(null);
    const [showInstructions, setShowInstructions] = useState(false);
    const [eventMessage, setEventMessage] = useState("");
    const [isFrontCamera, setIsFrontCamera] = useState(true); // 👈 Default to front camera
    const [stream, setStream] = useState(null);               // 👈 To manage stopping/starting

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [streaming, setStreaming] = useState(false);
    // State for individual instruction sections visibility
    const [showProperForm, setShowProperForm] = useState(false);
    const [showAngleDetails, setShowAngleDetails] = useState(false);
    const [showMistakes, setShowMistakes] = useState(false);
    const [showBenefits, setShowBenefits] = useState(false);
    const [showSetup, setShowSetup] = useState(false);

    // Function to get the appropriate GIF based on exercise type
    const getExerciseGif = () => {
        switch (exercise) {
            case "bicep_curl_right":
                return bicepCurlRightGif;
            case "bicep_curl_left":
                return bicepCurlLeftGif;
            case "lateral_raise_right":
                return lateralRaiseRightGif;
            case "lateral_raise_left":
                return lateralRaiseLeftGif;
            case "front_raise_right":
                return frontRaiseRightGif;
            case "front_raise_left":
                return frontRaiseRightGif; // Use right GIF and mirror it
            case "overhead_press_right":
                return overheadPressRightGif;
            case "overhead_press_left":
                return overheadPressRightGif; // Use right GIF and mirror it
            case "single_arm_dumbbell_right":
                return singleArmDumbbellGif; // Mirror for right
            case "single_arm_dumbbell_left":
                return singleArmDumbbellGif; // Original for left

            default:
                return null;
        }
    };

    const formatExerciseTitle = (exercise) => {
        return exercise.replace(/_/g, " ").replace(/(^\w|\s\w)/g, (m) => m.toUpperCase());
    };

    // Function to get detailed instructions based on exercise type
    const getExerciseInstructions = () => {
        if (exercise.includes("bicep_curl")) {
            return {
                title: "Bicep Curl",
                properForm: [
                    "Hold a dumbbell in the target hand with arm fully extended",
                    "Keep your elbow close to your torso - this is your starting position",
                    "Curl the weight upward by bending at the elbow until your forearm is nearly vertical",
                    "Slowly lower the weight back to the starting position",
                    "Repeat for the desired number of repetitions"
                ],
                angleDetails: [
                    "Starting Position (Down): Arm nearly straight with angle > 160° between shoulder, elbow, and wrist",
                    "End Position (Up): Arm bent with angle < 30° between shoulder, elbow, and wrist",
                    "Rep Counted: When you move from the down position (>160°) to the up position (<30°) and back"
                ],
                mistakes: [
                    "Swinging the arm or using momentum",
                    "Moving the elbow away from the body",
                    "Not maintaining proper posture (leaning back)",
                    "Curling too quickly"
                ],
                benefits: [
                    "Strengthens biceps brachii muscles",
                    "Improves arm stability and grip strength",
                    "Enhances functional pulling movements"
                ]
            };
        }
        else if (exercise.includes("lateral_raise")) {
            return {
                title: "Lateral Raise",
                properForm: [
                    "Hold a dumbbell in the target hand with arm at your side",
                    "Maintain a slight bend in the elbow throughout the movement",
                    "Raise the arm out to the side until it's parallel to the floor",
                    "Briefly hold at the top position",
                    "Lower the weight slowly back to the starting position",
                    "Repeat for the desired number of repetitions"
                ],
                angleDetails: [
                    "Starting Position (Down): Arm close to body with minimal horizontal displacement from shoulder (< 0.1)",
                    "End Position (Up): Arm extended to the side with significant horizontal displacement from shoulder (> 0.2)",
                    "Rep Counted: When the wrist moves horizontally away from the shoulder beyond the threshold and returns"
                ],
                mistakes: [
                    "Using too much weight",
                    "Shrugging shoulders during the lift",
                    "Swinging the arm or using momentum",
                    "Raising the arm too high (above shoulder level)"
                ],
                benefits: [
                    "Targets the lateral deltoid muscles",
                    "Improves shoulder stability",
                    "Enhances upper body aesthetics",
                    "Strengthens shoulder joints"
                ]
            };
        }
        else if (exercise.includes("front_raise")) {
            return {
                title: "Front Raise",
                properForm: [
                    "Hold a dumbbell in the target hand with arm extended in front of your thigh",
                    "Keep a slight bend in the elbow with palm facing your body",
                    "Raise the arm forward and upward until it's parallel to the floor",
                    "Briefly hold at the top position",
                    "Lower the weight with control back to the starting position",
                    "Repeat for the desired number of repetitions"
                ],
                angleDetails: [
                    "Starting Position (Down): Small angle (< 20°) between wrist, shoulder, and waist with arm straight (elbow angle 130-180°)",
                    "End Position (Up): Large angle (> 70°) between wrist, shoulder, and waist",
                    "Proper Movement: Vertical movement must be greater than horizontal movement",
                    "Elbow Position: Maintain relatively straight arm (elbow angle between 130-180°)",
                    "Rep Counted: When arm moves from down position to up position while maintaining proper form"
                ],
                mistakes: [
                    "Using too much weight",
                    "Arching the back",
                    "Using momentum to swing the weight",
                    "Lifting the arm too high (above shoulder level)",
                    "Moving the arm sideways (like a lateral raise)"
                ],
                benefits: [
                    "Targets the anterior deltoid muscles",
                    "Strengthens shoulder joints",
                    "Improves posture and shoulder stability",
                    "Enhances pushing movements for daily activities"
                ]
            };
        }
        else if (exercise.includes("overhead_press")) {
            return {
                title: "Overhead Press",
                properForm: [
                    "Hold a dumbbell at shoulder height with elbow bent at 90 degrees",
                    "Ensure your palm is facing forward",
                    "Press the weight vertically upward until your arm is fully extended",
                    "Briefly hold at the top position",
                    "Lower the weight with control back to shoulder height",
                    "Repeat for the desired number of repetitions"
                ],
                angleDetails: [
                    "Starting Position (Down): 85-95° angle between shoulder, elbow, and wrist (approximately 90°)",
                    "End Position (Up): Arm nearly straight with angle > 165° between shoulder, elbow, and wrist",
                    "Vertical Alignment: Wrist must be aligned vertically with shoulder (horizontal difference < 0.1) and wrist positioned above shoulder",
                    "Rep Counted: When you move from down position (90°) to up position (>165°) while maintaining vertical alignment"
                ],
                mistakes: [
                    "Arching the back",
                    "Leaning to one side",
                    "Not pressing the weight vertically",
                    "Using momentum instead of controlled movement",
                    "Locking the elbow too hard at the top"
                ],
                benefits: [
                    "Develops shoulder and tricep strength",
                    "Improves core stability",
                    "Enhances overall upper body strength",
                    "Increases shoulder mobility"
                ]
            };
        }
        else if (exercise.includes("single_arm_dumbbell")) {
            return {
                title: "Single Arm Dumbbell Row",
                properForm: [
                    "Place one knee and the same-side hand on a bench",
                    "Keep your back flat and parallel to the floor",
                    "Hold a dumbbell in the free hand with arm fully extended",
                    "Pull the weight upward by bending your elbow and bringing it close to your body",
                    "Keep your elbow close to your torso during the movement",
                    "Lower the weight with control back to the starting position",
                    "Repeat for the desired number of repetitions"
                ],
                angleDetails: [
                    "Starting Position (Down): Arm nearly straight with angle > 160° between shoulder, elbow, and wrist",
                    "End Position (Up): Arm bent with angle < 40° between shoulder, elbow, and wrist",
                    "Rep Counted: When you move from the down position (>160°) to the up position (<40°) and back"
                ],
                mistakes: [
                    "Rounding the back",
                    "Rotating the torso during the pull",
                    "Not fully extending the arm at the bottom",
                    "Using momentum to swing the weight",
                    "Moving the elbow away from the body"
                ],
                benefits: [
                    "Builds strength in the latissimus dorsi, rhomboids, and biceps",
                    "Improves posture and back definition",
                    "Enhances grip strength",
                    "Develops unilateral (one-sided) strength"
                ]
            };
        }
        return {};
    };

    const handleSetTarget = async () => {
        const reps = parseInt(targetReps);
        if (reps <= 0 && targetReps !== "") {
            setErrorMessage("Please enter a valid number of target repetitions.");
            return;
        }

        try {
            await axios.post(
                "http://localhost:5000/api/set_target",
                {
                    target_reps: reps || 0,
                    exercise,
                },
                { withCredentials: true }
            );
            setContainerState(COLORS.TARGET_SET);
            setErrorMessage("");
        } catch (error) {
            console.error(error);
            setErrorMessage("Failed to set target repetitions. Please try again.");
        }
    };
    const startWebcam = async () => {
        try {
            // 🛑 Stop any previous stream
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }

            const constraints = {
                video: {
                    facingMode: isFrontCamera ? "user" : "environment"
                },
                audio: false
            };

            const newStream = await navigator.mediaDevices.getUserMedia(constraints);

            if (videoRef.current) {
                videoRef.current.srcObject = newStream;

                videoRef.current.onloadedmetadata = () => {
                    console.log("📸 onloadedmetadata triggered");
                    setStreaming(true);
                };

                setTimeout(() => {
                    if (!streaming) {
                        console.log("⏱️ Fallback: setting streaming to true");
                        setStreaming(true);
                    }
                }, 500);
            }

            setStream(newStream);
        } catch (err) {
            console.error("Webcam access error:", err);
            alert("Camera access failed. Please allow camera or try a different browser.");
        }
    };
    const handleToggleCamera = () => {
        setIsFrontCamera(prev => !prev); // ✅ Will restart webcam via useEffect
    };


    const handleStart = async () => {
        console.log("Sending to /api/start:", exercise);

        try {
            setIsFrontCamera(true); // Always start with front camera
            await axios.post(
                "http://localhost:5000/api/start",
                { exercise },
                { withCredentials: true }
            );

            setElapsedTime(0);
            setContainerState(COLORS.TRACKING);
            setTracking(true); // ✅ first set this — it will mount <video>

            const intervalId = setInterval(() => {
                setElapsedTime((prevTime) => prevTime + 1);
            }, 1000);

            setTimerId(intervalId);
        } catch (error) {
            console.error("START ERROR:", error);
            setErrorMessage("Failed to start exercise tracking. Please try again.");
        }
    };



    const handleStop = async () => {
        if (!window.confirm("Are you sure you want to stop this exercise?")) return;

        try {
            // ✅ Stop webcam
            if (videoRef.current?.srcObject) {
                const tracks = videoRef.current.srcObject.getTracks();
                tracks.forEach((track) => track.stop());
                videoRef.current.srcObject = null;
            }
            setStreaming(false);
            setTracking(false);

            // ✅ Your existing stop logic
            await axios.post(
                "http://localhost:5000/api/stop",
                {
                    exercise_name: exercise,
                    duration: elapsedTime,
                    reps: parseInt(targetReps) || 0,
                },
                { withCredentials: true }
            );

            clearInterval(timerId);
            setTimerId(null);
            setContainerState(COLORS.DEFAULT);
            setElapsedTime(0);
            window.location.reload();
        } catch (error) {
            console.error(error);
            setErrorMessage("Failed to stop exercise tracking. Please try again.");
        }
    };

    // Add debugging to identify where the issue occurs
    const sendFrameToBackend = async () => {
        console.log("🛰️ Sending frame to backend...");

        if (!videoRef.current || !canvasRef.current) {
            console.log("🚫 videoRef or canvasRef is null");
            return;
        }

        try {
            const context = canvasRef.current.getContext("2d");

            // Make sure video is playing and has dimensions before capturing
            if (!videoRef.current.videoWidth || !videoRef.current.videoHeight) {
                console.log("⚠️ Video dimensions not available yet");
                return;
            }

            // Set canvas size to match video
            canvasRef.current.width = videoRef.current.videoWidth;
            canvasRef.current.height = videoRef.current.videoHeight;

            // Draw video frame to canvas
            context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
            console.log(`🖼️ Frame captured: ${canvasRef.current.width}x${canvasRef.current.height}`);

            // Create blob from canvas
            canvasRef.current.toBlob(async (blob) => {
                if (!blob) {
                    console.error("Failed to create blob from canvas");
                    return;
                }

                console.log(`🧩 Blob created: ${blob.size} bytes`);
                const formData = new FormData();
                formData.append("frame", blob, "frame.jpg");

                try {
                    console.log("📤 Sending request to backend...");
                    const response = await axios.post(
                        "http://localhost:5000/api/process_frame",
                        formData,
                        {
                            responseType: "blob",
                            withCredentials: true,
                            headers: {
                                'Content-Type': 'multipart/form-data'
                            },
                            timeout: 5000 // Shorter timeout for faster feedback
                        }
                    );

                    console.log("📥 Response received:", response.status);

                    if (response.data && response.data.size > 0) {
                        console.log(`📊 Response data size: ${response.data.size} bytes`);
                        const imageUrl = URL.createObjectURL(response.data);
                        const imageElement = document.getElementById("processed-frame");
                        if (imageElement) {
                            imageElement.src = imageUrl;
                            imageElement.onload = () => console.log("🖼️ Image loaded successfully!");
                            imageElement.onerror = (e) => console.error("🚫 Image failed to load:", e);
                        } else {
                            console.error("❌ Image element not found");
                        }
                    } else {
                        console.error("Empty response data");
                        showErrorFrame("Empty Data");
                    }
                } catch (error) {
                    console.error("❌ Axios error:", error);
                    showErrorFrame(`Error: ${error.message}`);
                }
            }, "image/jpeg", 0.9);
        } catch (error) {
            console.error("❌ Canvas error:", error);
            showErrorFrame(`Canvas Error: ${error.message}`);
        }
    };

    // Helper function to show error message on the frame
    const showErrorFrame = (message) => {
        const imageElement = document.getElementById("processed-frame");
        if (imageElement) {
            const errorCanvas = document.createElement("canvas");
            errorCanvas.width = 640;
            errorCanvas.height = 480;
            const ctx = errorCanvas.getContext("2d");
            ctx.fillStyle = "black";
            ctx.fillRect(0, 0, 640, 480);
            ctx.fillStyle = "red";
            ctx.font = "20px Arial";
            ctx.fillText(message, 220, 240);
            ctx.fillText("Check console for details", 180, 280);

            imageElement.src = errorCanvas.toDataURL();
        }
    };
    const formatTime = (timeInSeconds) => {
        const minutes = Math.floor(timeInSeconds / 60);
        const seconds = timeInSeconds % 60;
        return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
    };
    useEffect(() => {
        if (tracking && videoRef.current) {
            console.log("🎬 Video DOM is ready, starting webcam (or restarting due to toggle)...");
            startWebcam();
        }

        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, [tracking, isFrontCamera]); // ✅ include isFrontCamera


    useEffect(() => {
        console.log("🎯 useEffect | tracking:", tracking, "| streaming:", streaming);
        let interval;
        if (tracking && streaming) {
            console.log("✅ Starting frame interval...");
            interval = setInterval(sendFrameToBackend, 200);
        }
        return () => {
            console.log("🛑 Clearing frame interval...");
            clearInterval(interval);
        };
    }, [tracking, streaming]);

    useEffect(() => {
        const getCamera = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            } catch (err) {
                console.error("Webcam error:", err);
            }
        };
        getCamera();
    }, []);

    useEffect(() => {
        let pollInterval;

        if (tracking) {
            pollInterval = setInterval(async () => {
                try {
                    const res = await axios.get("http://localhost:5000/api/get_event", {
                        withCredentials: true
                    });

                    if (res.data?.event) {
                        console.log("🎯 Event from backend:", res.data.event);
                        setEventMessage(res.data.event);

                        // 🔊 Speak it using browser TTS
                        const utterance = new SpeechSynthesisUtterance(res.data.event);
                        window.speechSynthesis.speak(utterance);

                    }
                } catch (err) {
                    console.error("Event polling failed:", err);
                }
            }, 5000);
        }

        return () => clearInterval(pollInterval);
    }, [tracking]);

    const exerciseGif = getExerciseGif();
    const exerciseInstructions = getExerciseInstructions();

    return (
        <div className={`exercise-container ${containerState}`}>
            <div className="exercise-grid">
                <div className="exercise-left-column">
                    <h1>{formatExerciseTitle(exercise)} Exercise</h1>

                    {!showInstructions && (
                        <button
                            className="instructions-toggle-btn"
                            onClick={() => setShowInstructions(true)}
                        >
                            Show Instructions
                        </button>
                    )}
                    {showInstructions && exerciseInstructions.title && (
                        <div className="detailed-instructions">
                            <h2>{exerciseInstructions.title} Instructions</h2>

                            <div className="instruction-section">
                                <div className="section-header">
                                    <h3>Proper Form</h3>
                                    <button
                                        className="detail-toggle-btn"
                                        onClick={() => setShowProperForm(!showProperForm)}
                                    >
                                        {showProperForm ? "Hide Details" : "Show Details"}
                                    </button>
                                </div>
                                {showProperForm && (
                                    <ol>
                                        {exerciseInstructions.properForm.map((step, index) => (
                                            <li key={`form-${index}`}>{step}</li>
                                        ))}
                                    </ol>
                                )}
                            </div>

                            <div className="instruction-section">
                                <div className="section-header">
                                    <h3>Angle Details</h3>
                                    <button
                                        className="detail-toggle-btn"
                                        onClick={() => setShowAngleDetails(!showAngleDetails)}
                                    >
                                        {showAngleDetails ? "Hide Details" : "Show Details"}
                                    </button>
                                </div>
                                {showAngleDetails && (
                                    <ul>
                                        {exerciseInstructions.angleDetails.map((detail, index) => (
                                            <li key={`angle-${index}`}>{detail}</li>
                                        ))}
                                    </ul>
                                )}
                            </div>

                            <div className="instruction-section">
                                <div className="section-header">
                                    <h3>Common Mistakes to Avoid</h3>
                                    <button
                                        className="detail-toggle-btn"
                                        onClick={() => setShowMistakes(!showMistakes)}
                                    >
                                        {showMistakes ? "Hide Details" : "Show Details"}
                                    </button>
                                </div>
                                {showMistakes && (
                                    <ul>
                                        {exerciseInstructions.mistakes.map((mistake, index) => (
                                            <li key={`mistake-${index}`}>{mistake}</li>
                                        ))}
                                    </ul>
                                )}
                            </div>

                            <div className="instruction-section">
                                <div className="section-header">
                                    <h3>Exercise Benefits</h3>
                                    <button
                                        className="detail-toggle-btn"
                                        onClick={() => setShowBenefits(!showBenefits)}
                                    >
                                        {showBenefits ? "Hide Details" : "Show Details"}
                                    </button>
                                </div>
                                {showBenefits && (
                                    <ul>
                                        {exerciseInstructions.benefits.map((benefit, index) => (
                                            <li key={`benefit-${index}`}>{benefit}</li>
                                        ))}
                                    </ul>
                                )}
                            </div>

                            {/* Basic setup instructions moved inside the detailed instructions */}
                            <div className="instruction-section">
                                <div className="section-header">
                                    <h3>Setup</h3>
                                    <button
                                        className="detail-toggle-btn"
                                        onClick={() => setShowSetup(!showSetup)}
                                    >
                                        {showSetup ? "Hide Details" : "Show Details"}
                                    </button>
                                </div>
                                {showSetup && (
                                    <ul>
                                        <li>Ensure you have enough space around you to perform the exercise safely.</li>
                                        <li>Stand about 1 meter away from the camera for better visibility.</li>
                                        <li>Ensure there is sufficient lighting in the room.</li>
                                        <li>Wear comfortable clothing that allows you to move freely.</li>
                                    </ul>
                                )}
                            </div>
                            {/* Toggle button for instructions */}
                            <button
                                className="instructions-toggle-btn"
                                onClick={() => setShowInstructions(false)}
                            >
                                Hide Instructions 🔼
                            </button>
                        </div>
                    )}

                    {/* Display the exercise GIF if available */}
                    {exerciseGif && (
                        <div className="exercise-demo">
                            <h2>Exercise Demonstration</h2>
                            <img
                                src={exerciseGif}
                                alt={`${formatExerciseTitle(exercise)} demonstration`}
                                className={`exercise-gif 
                                    ${["lateral_raise_left", "lateral_raise_right", "front_raise_left", "front_raise_right", "overhead_press_left", "overhead_press_right", "single_arm_dumbbell_left", "single_arm_dumbbell_right"].includes(exercise) ? "lateral-raise" : ""} 
                                    ${["front_raise_left", "overhead_press_left", "single_arm_dumbbell_right"].includes(exercise) ? "mirrored" : ""}`
                                }
                            />
                        </div>
                    )}

                    {/* Move control elements to the left column */}
                    <div className="exercise-controls">
                        <div className="target-input">
                            <label>Target Reps (Optional):</label>
                            <input
                                type="text"
                                value={targetReps}
                                onChange={(e) => {
                                    const value = e.target.value;
                                    setTargetReps(value === '' ? '' : parseInt(value) || '');
                                }}
                                placeholder="Enter reps(<50)"
                            />
                            <button onClick={handleSetTarget}>Set Target</button>
                        </div>

                        {errorMessage && <div className="error-message">{errorMessage}</div>}

                        <div className="buttons">
                            <button onClick={handleStart} disabled={tracking}>Start</button>
                            <button onClick={handleStop} disabled={!tracking}>Stop</button>
                        </div>

                        <div className="stopwatch">
                            <h2>Time: {formatTime(elapsedTime)}</h2>
                        </div>
                    </div>
                </div>

                <div className="exercise-right-column">
                    {tracking && (
                        <div className="video-and-angle">
                            <h2>Processed Video Feed</h2>

                            <video
                                ref={videoRef}
                                width="160"
                                height="120"
                                autoPlay
                                muted
                                onCanPlay={() => setStreaming(true)}
                                style={{ border: "1px solid gray", borderRadius: "4px" }}
                            />

                            <canvas
                                ref={canvasRef}
                                width="640"
                                height="480"
                                style={{ display: "none" }}
                            />

                            <img
                                id="processed-frame"
                                alt="Processed Frame"
                                width="640"
                                height="480"
                                style={{ border: "2px solid #000", borderRadius: "8px" }}
                            />
                            {eventMessage && (
                                <div className="event-feedback">
                                    <strong>🗣️ {eventMessage}</strong>
                                </div>
                            )}
                            <button className="camera-toggle-btn" onClick={handleToggleCamera}>
                                🔄 Switch to {isFrontCamera ? "Back" : "Front"} Camera
                            </button>

                        </div>
                    )}
                    {!tracking && (
                        <div className="video-placeholder">
                            <h2>Video Feed Will Appear Here</h2>
                            <p>Press the Start button to begin tracking your exercise</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Exercise;