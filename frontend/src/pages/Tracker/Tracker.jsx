// frontend/src/pages/Tracker/Tracker.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // Using navigate for potential redirect
import { getSessionSummary, updateTaskStatus } from '../../api/api';
import { useSession } from '../../hooks/useSession';
import Loader from '../../components/Loader/Loader';
import Card from '../../components/Card/Card';
import Button from '../../components/Button/Button'; // For a 'Select Track' button or similar
import styles from './Tracker.module.css';

const Tracker = () => {
  const [sessionData, setSessionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { sessionId } = useSession();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSessionData = async () => {
      if (!sessionId) {
        setError("Session not found. Please start from Domain Selection.");
        setLoading(false);
        return;
      }
      try {
        const data = await getSessionSummary(sessionId);
        setSessionData(data);
      } catch (err) {
        console.error('Error fetching session summary for tracker:', err);
        setError('Failed to load session data. ' + (err.response?.data?.detail || err.message));
      } finally {
        setLoading(false);
      }
    };
    fetchSessionData();
  }, [sessionId]);

  const handleTaskStatusChange = async (weekIndex, taskIndex, currentTask, isCompleted) => {
    if (!sessionId) return; // Should not happen if check above works

    const originalTask = currentTask.task; // The original task string
    const originalWeekNumber = sessionData.careerTracks[0].roadmap[weekIndex].week; // Assuming one track for now, get week number

    const taskUpdatePayload = {
      week: originalWeekNumber,
      task: originalTask,
      status: !isCompleted, // Toggle status
      resourceLink: currentTask.resourceLink // Include resourceLink in update
    };

    try {
      // API call to update single task status
      const updatedWeek = await updateTaskStatus(sessionId, taskUpdatePayload);
      
      // Update local state to reflect the change
      setSessionData(prevData => {
        if (!prevData) return prevData;

        const newCareerTracks = [...prevData.careerTracks];
        if (newCareerTracks[0] && newCareerTracks[0].roadmap) {
          const newRoadmap = [...newCareerTracks[0].roadmap];
          // Find the updated week by its week number, not just index
          const targetWeekIdx = newRoadmap.findIndex(w => w.week === updatedWeek.week);
          if (targetWeekIdx !== -1) {
            newRoadmap[targetWeekIdx] = updatedWeek; // Replace the old week with the updated one
          }
          newCareerTracks[0] = { ...newCareerTracks[0], roadmap: newRoadmap };
        }
        return { ...prevData, careerTracks: newCareerTracks };
      });
    } catch (err) {
      console.error('Error updating task status:', err);
      setError('Failed to update task. ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return <Loader />;
  }

  if (error) {
    return <p className={styles.errorMessage}>{error}</p>;
  }

  if (!sessionData || sessionData.careerTracks.length === 0 || !sessionData.careerTracks[0].roadmap || sessionData.careerTracks[0].roadmap.length === 0) {
    return (
      <div className={styles.emptyState}>
        <p>No active roadmap found. Please ensure you have selected a domain, completed the quiz, and generated a roadmap.</p>
        <Button onClick={() => navigate('/')}>Start New Journey</Button>
      </div>
    );
  }

  const activeRoadmap = sessionData.careerTracks[0].roadmap;
  const activeTrackTitle = sessionData.careerTracks[0].title;

  return (
    <div className={styles.trackerContainer}>
      <h2 className={styles.pageTitle}>Progress Tracker for: {activeTrackTitle}</h2>
      <div className={styles.weeksGrid}>
        {activeRoadmap.map((week, weekIndex) => (
          <Card key={week.week} title={`Week ${week.week}`} className={styles.weekCard}>
            <ul className={styles.taskList}>
              {week.tasks.map((task, taskIndex) => (
                <li key={taskIndex} className={styles.taskItem}>
                  <input
                    type="checkbox"
                    checked={task.isCompleted}
                    onChange={() => handleTaskStatusChange(weekIndex, taskIndex, task, task.isCompleted)}
                    className={styles.taskCheckbox}
                  />
                  <span className={`${styles.taskText} ${task.isCompleted ? styles.completed : ''}`}>
                    {task.task}
                  </span>
                  {task.resourceLink && (
                    <a
                      href={task.resourceLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={styles.resourceLink}
                    >
                      (Resource)
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Tracker;