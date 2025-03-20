import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ProgressPage.css";

const ProgressPage = () => {
  const [exerciseList, setExerciseList] = useState([]); // List of exercises
  const [selectedExercise, setSelectedExercise] = useState(""); // Selected exercise
  const [progressData, setProgressData] = useState([]); // Progress data for selected exercise
  const [errorMessage, setErrorMessage] = useState(""); // Error messages
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]); // Default to today's date
  const [isLoading, setIsLoading] = useState(false); // Loading state

  // Fetch available exercises when the component loads
  useEffect(() => {
    const fetchExercises = async () => {
      try {
        const response = await axios.get("http://localhost:5000/api/get_exercises", {
          withCredentials: true, // Include cookies for session
        });
        setExerciseList(response.data);
        if (response.data.length > 0) {
          setSelectedExercise(response.data[0]); // Default to the first exercise
        }
      } catch (error) {
        console.error("Failed to fetch exercises:", error);
        setErrorMessage("Failed to load exercises. Please try again.");
      }
    };

    fetchExercises();
  }, []);

  // Fetch progress data when date or exercise changes
  useEffect(() => {
    if (!selectedExercise) return;

    const fetchProgress = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get("http://localhost:5000/api/get_progress", {
          params: { date, exercise_name: selectedExercise },
          withCredentials: true, // Include cookies for session
        });

        if (response.data.length === 0) {
          setProgressData([]);
          setErrorMessage(`No progress data available for ${selectedExercise} on ${date}.`);
        } else {
          setProgressData(response.data);
          setErrorMessage("");
        }
      } catch (error) {
        console.error("Failed to fetch progress data:", error);
        setErrorMessage("Failed to load progress data. Please check your connection or try again.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProgress();
  }, [date, selectedExercise]);

  return (
    <div className="progress-page">
      <h1>Progress</h1>

      {/* Exercise Selector */}
      <div className="exercise-selector">
        <label htmlFor="exercise">Select Exercise:</label>
        <select
          id="exercise"
          value={selectedExercise}
          onChange={(e) => setSelectedExercise(e.target.value)}
        >
          {exerciseList.map((exercise, index) => (
            <option key={index} value={exercise}>
              {exercise.replace(/_/g, " ")} {/* Format exercise names */}
            </option>
          ))}
        </select>
      </div>

      {/* Date Picker */}
      <div className="date-picker">
        <label htmlFor="date">Select Date:</label>
        <input
          id="date"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
      </div>

      {/* Loading or Error Messages */}
      {isLoading ? (
        <div className="loading-message">Loading progress data...</div>
      ) : errorMessage ? (
        <div className="error-message">{errorMessage}</div>
      ) : null}

      {/* Progress List */}
      <div className="progress-list">
        {progressData.length > 0 && (
          <div className="progress-item">
            <h3>{selectedExercise.replace(/_/g, " ")}</h3>
            <p>Reps: {progressData[0]?.reps}</p>
            <p>Duration: {progressData[0]?.duration} seconds</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressPage;
