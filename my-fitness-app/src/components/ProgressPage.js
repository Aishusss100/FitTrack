import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ProgressPage.css";

const ProgressPage = () => {
  const [exerciseList, setExerciseList] = useState([]);
  const [selectedExercise, setSelectedExercise] = useState("");
  const [viewType, setViewType] = useState("daily");
  const [progressData, setProgressData] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchExercises = async () => {
      try {
        const response = await axios.get("http://localhost:5000/api/get_exercises", {
          withCredentials: true,
        });
        setExerciseList(response.data);
        if (response.data.length > 0) {
          setSelectedExercise(response.data[0]);
        }
      } catch (error) {
        console.error("Failed to fetch exercises:", error);
        setErrorMessage("Failed to load exercises. Please try again.");
      }
    };

    fetchExercises();
  }, []);

  useEffect(() => {
    if (!selectedExercise) return;

    const fetchProgressData = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get("http://localhost:5000/api/get_progress", {
          params: { view_type: viewType, exercise_name: selectedExercise },
          withCredentials: true,
        });

        setProgressData(response.data);
        setErrorMessage("");
      } catch (error) {
        console.error("Failed to fetch progress data:", error);
        setErrorMessage("Failed to load progress data. Please check your connection.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProgressData();
  }, [viewType, selectedExercise]);

  // Function to determine progress status
  const getProgressStatus = (current, previous) => {
    if (!previous) return "🆕 First Entry"; // No previous data

    const currentEfficiency = current.reps / current.duration;
    const previousEfficiency = previous.reps / previous.duration;

    if (currentEfficiency > previousEfficiency) return "🟢 Improved";
    if (currentEfficiency < previousEfficiency) return "🔴 Needs Improvement";
    return "🟡 No Change";
  };

  return (
    <div className="progress-page">
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
              {exercise.replace(/_/g, " ")}
            </option>
          ))}
        </select>
      </div>

      {/* View Selector */}
      <div className="view-selector">
        <button className={viewType === "daily" ? "active" : ""} onClick={() => setViewType("daily")}>Daily</button>
        <button className={viewType === "weekly" ? "active" : ""} onClick={() => setViewType("weekly")}>Weekly</button>
        <button className={viewType === "monthly" ? "active" : ""} onClick={() => setViewType("monthly")}>Monthly</button>
      </div>

      {/* Loading Indicator */}
      {isLoading && <div className="loading-message">Loading...</div>}

      {/* Error Messages */}
      {errorMessage && <div className="error-message">{errorMessage}</div>}

      {/* Progress Data */}
      {!isLoading && progressData.length > 0 && (
        <div className="progress-list">
          {progressData.map((entry, index) => {
            const previousEntry = index > 0 ? progressData[index - 1] : null;
            const progressStatus = viewType !== "daily" ? getProgressStatus(entry, previousEntry) : null;

            return (
              <div key={index} className="progress-item">
                <p><strong>Date:</strong> {entry.date}</p>
                <p><strong>Reps:</strong> {entry.reps}</p>
                <p><strong>Duration:</strong> {(entry.duration / 60).toFixed(2)} mins</p>
                <p><strong>Efficiency:</strong> {(entry.reps / entry.duration).toFixed(2)}</p>
                {viewType !== "daily" && (
                  <p className={`progress-status ${progressStatus.includes("Improved") ? "improved" : progressStatus.includes("Needs") ? "declined" : "no-change"}`}>
                    <strong>Progress:</strong> {progressStatus}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* No Data Message */}
      {!isLoading && progressData.length === 0 && !errorMessage && (
        <div className="no-data-message">No progress data available for this selection.</div>
      )}
    </div>
  );
};

export default ProgressPage;
