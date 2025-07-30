// frontend/src/pages/Roadmap/Roadmap.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getRoadmap } from '../../api/api';
import styles from './Roadmap.module.css';

const FullPageSpinner = () => (
    <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
    </div>
);

const Roadmap = () => {
    const { trackId } = useParams();
    const [roadmap, setRoadmap] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // This state would be updated by user interaction in a full app
    const [tasksStatus, setTasksStatus] = useState({});

    useEffect(() => {
        const fetchRoadmap = async () => {
            if (!trackId) {
                setError("No track ID provided for roadmap.");
                setLoading(false);
                return;
            }
            try {
                const data = await getRoadmap(trackId);
                setRoadmap(data);
                // Initialize local task completion state from fetched data
                const initialStatus = {};
                data.forEach((week, weekIndex) => {
                    week.tasks.forEach((task, taskIndex) => {
                        initialStatus[`${weekIndex}-${taskIndex}`] = task.isCompleted;
                    });
                });
                setTasksStatus(initialStatus);
            } catch (err) {
                console.error('Error fetching roadmap:', err);
                setError('Failed to load roadmap. ' + (err.response?.data?.detail || err.message));
            } finally {
                setLoading(false);
            }
        };

        fetchRoadmap();
    }, [trackId]);

    const handleCheckboxChange = (weekIndex, taskIndex) => {
        // This is where you would also call an API to save the state
        const key = `${weekIndex}-${taskIndex}`;
        setTasksStatus(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const getWeekStatus = (week, weekIndex) => {
        const totalTasks = week.tasks.length;
        if (totalTasks === 0) return 'pending';
        
        const completedTasks = week.tasks.filter((task, taskIndex) => tasksStatus[`${weekIndex}-${taskIndex}`]).length;

        if (completedTasks === totalTasks) return 'completed';
        if (completedTasks > 0) return 'active';
        return 'pending';
    };

    const getBulletContent = (status) => {
        return status === 'completed' ? '✓' : '';
    };

    const getBulletClass = (status) => {
        if (status === 'completed') return styles.bulletCompleted;
        if (status === 'active') return styles.bulletActive;
        return styles.bulletPending;
    };

    if (loading) {
        return <FullPageSpinner />;
    }

    if (error) {
        return <div className={styles.centeredMessageContainer}><div className={styles.errorMessage}>⚠️ {error}</div></div>;
    }

    if (roadmap.length === 0) {
        return <div className={styles.centeredMessageContainer}><div className={styles.emptyState}>No roadmap generated for this track yet.</div></div>;
    }

    return (
        <div className={styles.roadmapContainer}>
            <h2 className={styles.pageTitle}>Your Personalized Roadmap 🗺️</h2>
            
            <div className={styles.timeline}>
                {roadmap.map((week, weekIndex) => {
                    const status = getWeekStatus(week, weekIndex);
                    
                    return (
                        <div key={week.week} className={styles.timelineItem}>
                            <div className={`${styles.timelineBullet} ${getBulletClass(status)}`}>
                                {getBulletContent(status)}
                            </div>
                            
                            <div className={styles.weekContent}>
                                <h3 className={styles.weekTitle}>Week {week.week}</h3>
                                
                                {week.tasks.length > 0 ? (
                                    <ul className={styles.taskList}>
                                        {week.tasks.map((task, taskIndex) => (
                                            <li key={taskIndex} className={styles.taskItem}>
                                                <label className={styles.taskLabel}>
                                                    <input
                                                        type="checkbox"
                                                        checked={tasksStatus[`${weekIndex}-${taskIndex}`] || false}
                                                        onChange={() => handleCheckboxChange(weekIndex, taskIndex)}
                                                        className={styles.taskCheckbox}
                                                    />
                                                    <span className={styles.taskText}>{task.task}</span>
                                                </label>
                                                
                                                {task.resourceLink && (
                                                    <a
                                                        href={task.resourceLink}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className={styles.resourceLink}
                                                    >
                                                        Resource ↗
                                                    </a>
                                                )}
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className={styles.noTasks}>No tasks for this week.</p>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default Roadmap;