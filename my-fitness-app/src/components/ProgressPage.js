import React, { useEffect, useState } from "react";
import { Line, Bar, Pie } from "react-chartjs-2"; // Chart components
import axios from "axios";
import "./ProgressPage.css";

const ProgressPage = () => {
  const [exerciseList, setExerciseList] = useState([]); // List of exercises
  const [selectedExercise, setSelectedExercise] = useState(""); // Selected exercise
  const [viewType, setViewType] = useState("daily"); // Default view: "daily"
  const [chartData, setChartData] = useState({}); // Data for the charts
  const [isLoading, setIsLoading] = useState(false); // Loading state
  const [errorMessage, setErrorMessage] = useState(""); // Error messages

  // Fetch list of available exercises when the component loads
  useEffect(() => {
    const fetchExercises = async () => {
      try {
        const response = await axios.get("http://localhost:5000/api/get_exercises", {
          withCredentials: true,
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

  // Fetch progress data for the selected exercise and view type
  useEffect(() => {
    if (!selectedExercise) return;

    const fetchProgressData = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get("http://localhost:5000/api/get_progress", {
          params: { view_type: viewType, exercise_name: selectedExercise },
          withCredentials: true,
        });

        const labels = response.data.map((data) => data.date); // X-axis: Dates
        const repsData = response.data.map((data) => data.reps); // Y-axis: Reps
        const durationData = response.data.map((data) => data.duration / 60); // Y-axis: Duration (in mins)

        if (viewType === "monthly") {
          setChartData({
            labels,
            datasets: [
              {
                label: "Reps",
                data: repsData,
                borderColor: "#4a90e2",
                backgroundColor: "rgba(74, 144, 226, 0.2)",
                fill: true,
              },
              {
                label: "Time (mins)",
                data: durationData,
                borderColor: "#f78fb3",
                backgroundColor: "rgba(247, 143, 179, 0.2)",
                fill: true,
              },
            ],
          });
        } else if (viewType === "weekly") {
          setChartData({
            labels,
            datasets: [
              {
                label: "Reps",
                data: repsData,
                backgroundColor: "rgba(214, 40, 57, 0.6)",
                borderColor: "#d62839",
                borderWidth: 1,
              },
              {
                label: "Time (mins)",
                data: durationData,
                backgroundColor: "rgba(74, 144, 226, 0.6)",
                borderColor: "#4a90e2",
                borderWidth: 1,
              },
            ],
          });
        } else if (viewType === "daily") {
          setChartData({
            labels: ["Reps", "Duration (mins)"],
            datasets: [
              {
                data: [repsData[0], durationData[0]],
                backgroundColor: ["#f9c74f", "#43aa8b"],
              },
            ],
          });
        }

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

  return (
    <div className="progress-page">
      <h1>Progress Tracker</h1>

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

      {/* View Selector Tabs */}
      <div className="view-selector">
        <button
          className={viewType === "daily" ? "active" : ""}
          onClick={() => setViewType("daily")}
        >
          Daily
        </button>
        <button
          className={viewType === "weekly" ? "active" : ""}
          onClick={() => setViewType("weekly")}
        >
          Weekly
        </button>
        <button
          className={viewType === "monthly" ? "active" : ""}
          onClick={() => setViewType("monthly")}
        >
          Monthly
        </button>
      </div>

      {/* Charts */}
      <div className="chart-container">
        {isLoading ? (
          <div className="loading-message">Loading chart...</div>
        ) : viewType === "monthly" ? (
          <Line data={chartData} />
        ) : viewType === "weekly" ? (
          <Bar data={chartData} />
        ) : viewType === "daily" ? (
          <Pie data={chartData} />
        ) : null}
      </div>

      {/* Error Messages */}
      {errorMessage && <div className="error-message">{errorMessage}</div>}
    </div>
  );
};

export default ProgressPage;
