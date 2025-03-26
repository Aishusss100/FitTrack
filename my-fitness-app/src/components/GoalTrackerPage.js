import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './GoalTrackerPage.css'; 

const ProgressBar = ({ value, max = 100, color = 'linear-gradient(to right, #d4af7a, #f5e1c8)' }) => {
  const progressWidth = Math.min(Math.max(value, 0), 100);
  return (
    <div className="progress-container">
      <div 
        className="progress-bar" 
        style={{ 
          width: `${progressWidth}%`, 
          background: color,
          transition: 'width 0.5s ease-in-out'
        }}
      />
    </div>
  );
};

const GoalTrackerPage = () => {
  const [activeGoals, setActiveGoals] = useState([]);
  const [achievedGoals, setAchievedGoals] = useState([]);
  const [goalProgress, setGoalProgress] = useState({});
  const [newGoal, setNewGoal] = useState({
    exercise_name: '',
    target_reps: '',
    target_duration: '',
    days_to_complete: '',
  });
  const [exercises, setExercises] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch active goals (is_achieved = 0)
        const activeGoalsResponse = await axios.get('http://localhost:5000/api/get_goals?is_achieved=0', { withCredentials: true });
        const activeGoalsList = activeGoalsResponse.data;
        
        // Fetch achieved goals
        const achievedGoalsResponse = await axios.get('http://localhost:5000/api/get_achieved_goals', { withCredentials: true });
        const achievedGoalsList = achievedGoalsResponse.data;
        
        // Fetch progress for each active goal and check if any have been achieved
        const progressPromises = activeGoalsList.map(async goal => {
          const progressResponse = await axios.get(`http://localhost:5000/api/check_goal_progress?goal_id=${goal.id}`, { withCredentials: true });
          return { goal, progress: progressResponse.data };
        });
        
        const progressResults = await Promise.all(progressPromises);
        
        // Separate active and achieved goals
        const newActiveGoals = [];
        const newGoalProgress = {};

        progressResults.forEach(({ goal, progress }) => {
          newGoalProgress[goal.id] = progress;
          
          if (progress.is_achieved) {
            // Add to achieved goals in the backend
            axios.post('http://localhost:5000/api/update_goal_status', {
              id: goal.id,
              is_achieved: 1
            }, { withCredentials: true });
          } else {
            newActiveGoals.push(goal);
          }
        });

        setActiveGoals(newActiveGoals);
        setAchievedGoals(achievedGoalsList);
        setGoalProgress(newGoalProgress);

        // Fetch list of exercises
        const exercisesResponse = await axios.get('http://localhost:5000/api/get_exercises', { withCredentials: true });
        setExercises(exercisesResponse.data);

        setError(null);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to fetch data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Refresh progress every minute
    const progressInterval = setInterval(fetchData, 60000);
    return () => clearInterval(progressInterval);
  }, []);

  const handleCreateGoal = async () => {
    // Validation checks (same as before)
    if (!newGoal.exercise_name) {
      alert("Please select an exercise");
      return;
    }

    if (!newGoal.target_reps || parseInt(newGoal.target_reps) <= 0) {
      alert("Target reps must be greater than 0");
      return;
    }

    if (!newGoal.target_duration || parseInt(newGoal.target_duration) <= 0) {
      alert("Target duration must be greater than 0");
      return;
    }

    if (!newGoal.days_to_complete) {
      alert("Please select days to complete");
      return;
    }

    try {
      await axios.post('http://localhost:5000/api/create_goal', {
        ...newGoal,
        target_reps: parseInt(newGoal.target_reps),
        target_duration: parseInt(newGoal.target_duration)
      }, { withCredentials: true });
      
      // Refresh active goals
      const activeGoalsResponse = await axios.get('http://localhost:5000/api/get_goals?is_achieved=0', { withCredentials: true });
      setActiveGoals(activeGoalsResponse.data);

      // Reset the new goal form
      setNewGoal({
        exercise_name: '',
        target_reps: '',
        target_duration: '',
        days_to_complete: '',
      });

      alert("Goal created successfully!");
    } catch (err) {
      console.error("Error creating goal:", err);
      alert("Failed to create goal. Please try again.");
    }
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div className="goal-tracking-container">
      {/* Create New Goal Section */}
      <div className="set-goals-section">
        <h2>Create a New Goal</h2>
        <form className="add-goal-form">
          <label htmlFor="exercise_name">Exercise Name</label>
          <select
            id="exercise_name"
            value={newGoal.exercise_name}
            onChange={(e) => setNewGoal({ ...newGoal, exercise_name: e.target.value })}
          >
            <option value="">Select an exercise</option>
            {exercises.map((exercise, index) => (
              <option key={index} value={exercise}>
                {exercise}
              </option>
            ))}
          </select>
          <label htmlFor="target_reps">Target Reps</label>
          <input
            type="number"
            id="target_reps"
            placeholder="Enter target reps"
            value={newGoal.target_reps}
            onChange={(e) => setNewGoal({ ...newGoal, target_reps: e.target.value })}
          />
          <label htmlFor="target_duration">Target Duration (seconds)</label>
          <input
            type="number"
            id="target_duration"
            placeholder="Enter target duration"
            value={newGoal.target_duration}
            onChange={(e) => setNewGoal({ ...newGoal, target_duration: e.target.value })}
          />
          <label htmlFor="days_to_complete">Days to Complete</label>
          <select
            id="days_to_complete"
            value={newGoal.days_to_complete}
            onChange={(e) => setNewGoal({ ...newGoal, days_to_complete: e.target.value })}
          >
            <option value="">Select duration</option>
            <option value="7">1 Week</option>
            <option value="14">2 Weeks</option>
            <option value="30">1 Month</option>
          </select>
          <button type="button" onClick={handleCreateGoal}>Create Goal</button>
        </form>
      </div>

      {/* Goal Columns Section */}
      <div className="goal-columns">
        {/* Active Goals */}
        <div className="active-goals-container">
          <h2>Active Goals</h2>
          {activeGoals.length > 0 ? (
            activeGoals.map(goal => {
              const progress = goalProgress[goal.id] || {};
              return (
                <div key={goal.id} className="goal-card">
                  <h3>{goal.exercise_name}</h3>
                  <div>
                    <p>Reps Progress:</p>
                    <ProgressBar 
                      value={progress.reps_progress || 0} 
                    />
                    <p>{progress.current_reps || 0} / {goal.target_reps} reps</p>
                  </div>
                  <p>Days to Complete: {goal.days_to_complete}</p>
                  <p>Start Date: {goal.created_at}</p>
                  <p>End Date: {progress.end_date}</p>
                </div>
              );
            })
          ) : (
            <p className="empty-goals-message">No active goals to display.</p>
          )}
        </div>

        {/* Achieved Goals */}
        <div className="achieved-goals-container">
          <h2>Achieved Goals</h2>
          {achievedGoals.length > 0 ? (
            achievedGoals.map(goal => (
              <div key={goal.id} className="goal-card">
                <h3>{goal.exercise_name}</h3>
                <div>
                  <p>Total Reps: {goal.target_reps}</p>
                  <p>Total Duration: {goal.target_duration} seconds</p>
                </div>
                <p>Days to Complete: {goal.days_to_complete}</p>
                <p>Start Date: {goal.created_at}</p>
              </div>
            ))
          ) : (
            <p className="empty-goals-message">No achieved goals to display.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default GoalTrackerPage;