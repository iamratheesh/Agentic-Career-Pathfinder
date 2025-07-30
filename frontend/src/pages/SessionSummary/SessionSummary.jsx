// frontend/src/pages/SessionSummary/SessionSummary.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSessionSummary } from '../../api/api';
import { useSession } from '../../hooks/useSession';
import styles from './SessionSummary.module.css';

const FullPageSpinner = () => (
    <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
    </div>
);

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
                setSessionData(data);
            } catch (err) {
                console.error('Error fetching session summary:', err);
                setError('Failed to load session summary. ' + (err.response?.data?.detail || err.message));
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, [activeSessionId]);

    if (loading) {
        return <FullPageSpinner />;
    }

    if (error) {
        return <div className={styles.centeredMessageContainer}><p className={styles.errorMessage}>{error}</p></div>;
    }

    if (!sessionData) {
        return (
            <div className={styles.centeredMessageContainer}>
                <div className={styles.emptyState}>
                    <p>No data found for this session. It might not exist or be incomplete.</p>
                    <button onClick={() => navigate('/')} className={styles.actionButton}>Start New Journey</button>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.summaryContainer}>
            <div className={styles.sessionCard}>
                <h2 className={styles.mainTitle}>Full Session Summary</h2>
                <p><strong>Domain:</strong> {sessionData.domain}</p>
                <p><strong>Detected Level:</strong> {sessionData.level || 'Not yet determined'}</p>
                <p><strong>Started At:</strong> {new Date(sessionData.createdAt).toLocaleString()}</p>
            </div>

            <h3 className={styles.sectionTitle}>Recommended Career Tracks</h3>
            {sessionData.careerTracks.length === 0 ? (
                <p className={styles.emptySection}>No career tracks recommended yet.</p>
            ) : (
                <div className={styles.tracksGrid}>
                    {sessionData.careerTracks.map(track => (
                        <div key={track.trackId} className={styles.trackCard}>
                            <h4 className={styles.cardTitle}>{track.title}</h4>
                            <p><strong>Avg. Salary:</strong> {track.avgSalary}</p>
                            <p><strong>Skills:</strong> {track.skills.join(', ')}</p>
                            
                            {track.roadmap && track.roadmap.length > 0 && (
                                <div className={styles.roadmapSection}>
                                    <h5 className={styles.roadmapTitle}>Roadmap Preview:</h5>
                                    {track.roadmap.slice(0, 2).map(week => ( // Show first 2 weeks as a preview
                                        <div key={week.week} className={styles.roadmapWeek}>
                                            <h6>Week {week.week}</h6>
                                            <ul className={styles.taskList}>
                                                {week.tasks.slice(0, 3).map((task, taskIndex) => ( // Show first 3 tasks
                                                    <li key={taskIndex} className={styles.taskItem}>
                                                        <span className={task.isCompleted ? styles.completedTask : ''}>
                                                            {task.task}
                                                        </span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
            <div className={styles.actions}>
                <button onClick={() => navigate('/')} className={styles.actionButton}>Start Another Journey</button>
            </div>
        </div>
    );
};

export default SessionSummary;