import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getSessionSummary } from '../../api/api';
import { useSession } from '../../hooks/useSession';
import styles from './SessionSummary.module.css';
import Loader from '../../components/Loader/Loader';
import Button from '../../components/Button/Button'; 

const SessionSummary = () => {
    const { sessionId: paramSessionId } = useParams();
    const { sessionId: storedSessionId } = useSession();
    const navigate = useNavigate();

    const activeSessionId = paramSessionId || storedSessionId;

    const [sessionData, setSessionData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchSummary = async () => {
            if (!activeSessionId) {
                setError("No session ID found. Please start a new session or provide an ID in the URL.");
                setLoading(false);
                return;
            }
            try {
                const data = await getSessionSummary(activeSessionId);
                console.log('Fetched session data:', data); 
                setSessionData(data);
            } catch (err) {
                console.error('Error fetching session summary:', err);
                setError('Failed to load session summary. ' + (err.response?.data?.detail || err.message));
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, [activeSessionId, navigate]);

    if (loading) {
        return <Loader />; 
    }

    if (error) {
        return <div className={styles.centeredMessageContainer}><p className={styles.errorMessage}>⚠️ {error}</p></div>;
    }

    if (!sessionData) {
        return (
            <div className={styles.centeredMessageContainer}>
                <div className={styles.emptyState}>
                    <p>No data found for this session. It might not exist or be incomplete.</p>
                    <Button onClick={() => navigate('/')} className={styles.actionButton}>Start New Journey</Button>
                </div>
            </div>
        );
    }

    const enrolledTracks = sessionData.careerTracks.filter(track => track.isEnrolled);
    const otherTracks = sessionData.careerTracks.filter(track => !track.isEnrolled);

    return (
        <div className={styles.summaryContainer}>
            <div className={styles.sessionCard}>
                <h2 className={styles.mainTitle}>Learning  Details</h2>
                <p><strong>Domain:</strong> {sessionData.domain}</p>
                <p><strong>Detected Level:</strong> {sessionData.level || 'Not yet determined'}</p>
                <p><strong>Started At:</strong> {new Date(sessionData.createdAt).toLocaleString()}</p>
            </div>

            <h3 className={styles.sectionTitle}>Current Learning ✨</h3>
            {enrolledTracks.length === 0 ? (
                <p className={styles.emptySection}>You haven't enrolled in any tracks yet. Enroll in one from the "Other Interests" section below or the "Career Tracks" page.</p>
            ) : (
                <div className={styles.tracksGrid}>
                    {enrolledTracks.map(track => (
                        <div key={track.trackId} className={`${styles.trackCard} ${styles.enrolledCard}`}> {/* Use track.trackId */}
                            <h4 className={styles.cardTitle}>{track.title} <span className={styles.enrolledTag}>Enrolled</span></h4>
                            <p><strong>Avg. Salary:</strong> {track.avgSalary}</p>
                            <p><strong>Skills:</strong> {track.skills.join(', ')}</p>
                            <p><strong>Tools:</strong> {track.tools.join(', ')}</p>
                            <p><strong>Growth:</strong> {track.growth}</p>
                            
                            {track.roadmap && track.roadmap.length > 0 ? (
                                <div className={styles.roadmapSection}>
                                    <h5 className={styles.roadmapTitle}>Roadmap Preview:</h5>
                                    {track.roadmap.slice(0, 2).map(week => ( 
                                        <div key={week.week} className={styles.roadmapWeek}>
                                            <h6>Week {week.week}</h6>
                                            <ul className={styles.taskList}>
                                                {week.tasks.slice(0, 3).map((task, taskIndex) => ( 
                                                    <li key={taskIndex} className={styles.taskItem}>
                                                        <span className={task.isCompleted ? styles.completedTask : ''}>
                                                            {task.task}
                                                        </span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                    <Button onClick={() => navigate(`/roadmap/${track._id}`)} className={styles.viewFullRoadmapButton}> View Full Roadmap </Button> {/* Use Button component, track.trackId */}
                                </div>
                            ) : (
                                <div className={styles.roadmapSection}>
                                    <p className={styles.emptySection}>Roadmap not generated for this track.</p>
                                    <Button onClick={() => navigate(`/roadmap/${track._id}`)} className={styles.generateRoadmapButton}> Generate Roadmap </Button> {/* Use Button component, track.trackId */}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            <h3 className={styles.sectionTitle}>Other Interests 🤔</h3>
            {otherTracks.length === 0 ? (
                <p className={styles.emptySection}>No other career tracks were recommended.</p>
            ) : (
                <div className={styles.tracksGrid}>
                    {otherTracks.map(track => (
                        <div key={track.trackId} className={styles.trackCard}>
                            <h4 className={styles.cardTitle}>{track.title}</h4>
                            <p><strong>Avg. Salary:</strong> {track.avgSalary}</p>
                            <p><strong>Skills:</strong> {track.skills.join(', ')}</p>
                            <p><strong>Tools:</strong> {track.tools.join(', ')}</p>
                            <p><strong>Growth:</strong> {track.growth}</p>
                            
                            {track.roadmap && track.roadmap.length > 0 ? (
                                <div className={styles.roadmapSection}>
                                    <h5 className={styles.roadmapTitle}>Roadmap Preview:</h5>
                                    {track.roadmap.slice(0, 2).map(week => (
                                        <div key={week.week} className={styles.roadmapWeek}>
                                            <h6>Week {week.week}</h6>
                                            <ul className={styles.taskList}>
                                                {week.tasks.slice(0, 3).map((task, taskIndex) => (
                                                    <li key={taskIndex} className={styles.taskItem}>
                                                        <span className={task.isCompleted ? styles.completedTask : ''}>
                                                            {task.task}
                                                        </span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                    <Button onClick={() => navigate(`/roadmap/${track._id}`)} className={styles.viewFullRoadmapButton}> View Full Roadmap </Button> {/* Use Button component, track.trackId */}
                                </div>
                            ) : (
                                <div className={styles.roadmapSection}>
                                    <p className={styles.emptySection}>Roadmap not generated for this track.</p>
                                    <Button onClick={() => navigate(`/roadmap/${track._id}`)} className={styles.generateRoadmapButton}> Generate Roadmap </Button> {/* Use Button component, track.trackId */}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            <div className={styles.actions}>
                <Button onClick={() => navigate('/')} className={styles.actionButton}>Start Another Journey</Button>
               
            </div>
        </div>
    );
};

export default SessionSummary;