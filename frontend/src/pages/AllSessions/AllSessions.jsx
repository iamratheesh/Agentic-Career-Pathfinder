// frontend/src/pages/AllSessions/AllSessions.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllSessions } from '../../api/api';
import styles from './AllSessions.module.css';

// A full-page loading spinner
const FullPageSpinner = () => (
  <div className={styles.loadingContainer}>
    <div className={styles.loadingSpinner}></div>
  </div>
);

const AllSessions = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAllSessions = async () => {
      try {
        const data = await getAllSessions();
        // Sort sessions by creation date, newest first
        const sortedData = data.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        setSessions(sortedData);
      } catch (err) {
        console.error('Error fetching all sessions:', err);
        setError('Failed to load all sessions. ' + (err.response?.data?.detail || err.message));
      } finally {
        setLoading(false);
      }
    };
    fetchAllSessions();
  }, []);

  const handleViewSessionSummary = (sessionId) => {
    navigate(`/session-summary/${sessionId}`);
  };

  if (loading) {
    return <FullPageSpinner />;
  }

  if (error) {
    return <div className={styles.centeredMessageContainer}><p className={styles.errorMessage}>{error}</p></div>;
  }

  return (
    <div className={styles.allSessionsContainer}>
      <h2 className={styles.pageTitle}>All Previous Sessions 📚</h2>

      {sessions.length === 0 ? (
        <div className={styles.centeredMessageContainer}>
          <p className={styles.emptyState}>No sessions found in the database.</p>
        </div>
      ) : (
        <div className={styles.sessionsGrid}>
          {sessions.map((session) => (
            <div key={session.sessionId} className={styles.sessionCard}>
              <div className={styles.cardContent}>
                <p className={styles.cardText}><strong>Domain:</strong> {session.domain}</p>
                <p className={styles.cardText}><strong>Level:</strong> {session.level || 'N/A'}</p>
                <p className={styles.cardText}><strong>Created:</strong> {new Date(session.createdAt).toLocaleString('en-IN')}</p>
              </div>
              <button onClick={() => handleViewSessionSummary(session.sessionId)} className={styles.viewSummaryButton}>
                View Full Summary
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AllSessions;