import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRoadmap, updateTaskStatus, updateEnrollmentStatus } from '../../api/api';
import { useSession } from '../../hooks/useSession';
import styles from './Roadmap.module.css';
import Loader from '../../components/Loader/Loader';
import Button from '../../components/Button/Button';
const Roadmap = () => {
    const { trackId } = useParams();
    const { sessionId } = useSession();
    const navigate = useNavigate();

    const [careerTrackDetails, setCareerTrackDetails] = useState(null);
    const [roadmapWeeks, setRoadmapWeeks] = useState([]);
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [updatingEnrollment, setUpdatingEnrollment] = useState(false); 


    useEffect(() => {
        const fetchRoadmap = async () => {
            if (!trackId) {
                setError("No track ID provided for roadmap.");
                setLoading(false);
                return;
            }
            if (!sessionId) { 
                setError("Session not found. Please start from the Domain Selection.");
                setLoading(false);
                // navigate('/');
                return;
            }

            try {
                const response = await getRoadmap(trackId);
                setCareerTrackDetails(response.track);
                setRoadmapWeeks(JSON.parse(JSON.stringify(response.roadmap))); 
            } catch (err) {
                console.error('Error fetching roadmap:', err);
                setError('Failed to load roadmap. ' + (err.response?.data?.detail || err.message));
            } finally {
                setLoading(false);
            }
        };

        fetchRoadmap();
    }, [trackId, sessionId, navigate]);

    const handleCheckboxChange = async (weekIndex, taskIndex) => {
        if (!sessionId) {
            setError("Cannot update task: Session ID is missing. Please start a new session.");
            return;
        }
        
        const updatedRoadmapData = JSON.parse(JSON.stringify(roadmapWeeks)); 
        const currentTask = updatedRoadmapData[weekIndex].tasks[taskIndex];
        const newStatus = !currentTask.isCompleted;
        currentTask.isCompleted = newStatus;
        setRoadmapWeeks(updatedRoadmapData); 

        const taskUpdatePayload = {
            week: updatedRoadmapData[weekIndex].week,
            task: currentTask.task,
            status: newStatus,
            resourceLink: currentTask.resourceLink
        };

        try {
            await updateTaskStatus(sessionId, taskUpdatePayload);
        } catch (err) {
            console.error('Error updating task status:', err);
            setError('Failed to update task status. Please try again. ' + (err.response?.data?.detail || err.message));
            currentTask.isCompleted = !newStatus;
            setRoadmapWeeks(JSON.parse(JSON.stringify(updatedRoadmapData)));
        }
    };

    const handleEnrollToggle = async () => {
        if (!sessionId || !trackId) {
            setError("Cannot enroll: Session or Track ID is missing.");
            return;
        }
        setUpdatingEnrollment(true);
        setError(null);

        try {
            const newEnrollmentStatus = !careerTrackDetails.isEnrolled;
            const updatedTrack = await updateEnrollmentStatus(trackId, newEnrollmentStatus);
            
            setCareerTrackDetails(prevDetails => ({
                ...prevDetails,
                isEnrolled: updatedTrack.isEnrolled
            }));

        } catch (err) {
            console.error('Error updating enrollment status:', err);
            setError('Failed to update enrollment status. ' + (err.response?.data?.detail || err.message));
        } finally {
            setUpdatingEnrollment(false);
        }
    };


    const getWeekStatus = (week) => {
        const totalTasks = week.tasks.length;
        if (totalTasks === 0) return 'pending';
        
        const completedTasks = week.tasks.filter(task => task.isCompleted).length;

        if (completedTasks === totalTasks) return 'completed';
        if (completedTasks > 0) return 'active';
        return 'pending';
    };

    const getBulletClass = (status) => {
        if (status === 'completed') return styles.bulletCompleted;
        if (status === 'active') return styles.bulletActive;
        return styles.bulletPending;
    };

    if (loading) {
        return <Loader />;
    }

    if (error) {
        return <div className={styles.centeredMessageContainer}><div className={styles.errorMessage}>⚠️ {error}</div></div>;
    }

    if (!careerTrackDetails) {
        return <div className={styles.centeredMessageContainer}><div className={styles.emptyState}>No track details found.</div></div>;
    }

    if (roadmapWeeks.length === 0) {
        return (
            <div className={styles.roadmapContainer}>
                <h2 className={styles.pageTitle}>Roadmap for: {careerTrackDetails.title} 🗺️</h2>
                
                <div className={styles.enrollmentStatus}>
                    <span>Current Status: <strong className={`${careerTrackDetails.isEnrolled ? styles.isEnrolled : styles.isNotEnrolled}`}>{careerTrackDetails.isEnrolled ? 'Enrolled' : 'Not Enrolled'}</strong></span>
                    <Button
                        onClick={handleEnrollToggle}
                        disabled={updatingEnrollment}
                        variant={careerTrackDetails.isEnrolled ? 'secondary' : 'primary'}
                        className={styles.enrollButton}
                    >
                        {updatingEnrollment ? 'Updating...' : (careerTrackDetails.isEnrolled ? 'Unenroll' : 'Enroll')}
                    </Button>
                </div>
                <div className={styles.centeredMessageContainer}><div className={styles.emptyState}>No roadmap generated for this track yet.</div></div>
            </div>
        );
    }

    return (
        <div className={styles.roadmapContainer}>
            <h2 className={styles.pageTitle}>Roadmap for: {careerTrackDetails.title} 🗺️</h2>
            {!careerTrackDetails.isEnrolled && (
 <div className={styles.enrollmentStatus}>
                <span>Current Status: <strong>{careerTrackDetails.isEnrolled ? 'Enrolled' : 'Not Enrolled'}</strong></span>
                <Button
                    onClick={handleEnrollToggle}
                    disabled={updatingEnrollment}
                    variant={careerTrackDetails.isEnrolled ? 'secondary' : 'primary'}
                    className={styles.enrollButton}
                >
                    {updatingEnrollment ? 'Updating...' : (careerTrackDetails.isEnrolled ? 'Unenroll' : 'Enroll')}
                </Button>
            </div>
            )}
           
            
            <div className={styles.timeline}>
                {roadmapWeeks.map((week, weekIndex) => {
                    const status = getWeekStatus(week);
                    
                    return (
                        <div key={week.week} className={`${styles.timelineItem} ${getBulletClass(status)} ${status === "completed" ? styles.markCompleted : ''}`}>
                            <div className={styles.weekContent}>
                                <h3 className={styles.weekTitle}>Week {week.week}</h3>
                                
                                {week.tasks.length > 0 ? (
                                    <ul className={styles.taskList}>
                                        {week.tasks.map((task, taskIndex) => (
                                            <li key={taskIndex} className={styles.taskItem}>
                                                <label className={styles.taskLabel}>
                                                    <input
                                                        type="checkbox"
                                                        checked={task.isCompleted || false}
                                                        onChange={() => handleCheckboxChange(weekIndex, taskIndex)}
                                                        className={styles.taskCheckbox}
                                                    />
                                                    <span className={`${styles.taskText} ${task.isCompleted ? styles.taskCompletedText : ''}`}>
                                                        {task.task}
                                                    </span>
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