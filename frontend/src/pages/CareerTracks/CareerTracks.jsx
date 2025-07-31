import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCareerTracks } from '../../api/api';
import { useSession } from '../../hooks/useSession';
import styles from './CareerTracks.module.css';
import Loader from '../../components/Loader/Loader';



const CareerTracks = () => {
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { sessionId } = useSession();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCareerTracks = async () => {
      if (!sessionId) {
        setError("Session not found. Please start from the Domain Selection.");
        setLoading(false);
        return;
      }
      try {
        const data = await getCareerTracks(sessionId);
        setTracks(data);
      } catch (err) {
        console.error('Error fetching career tracks:', err);
        setError('Failed to load career tracks. ' + (err.response?.data?.detail || err.message));
      } finally {
        setLoading(false);
      }
    };

    fetchCareerTracks();
  }, [sessionId]);

  const handleViewRoadmap = (trackId) => {
    navigate(`/roadmap/${trackId}`);
  };

  if (loading) {
    return <Loader />;
  }

  if (error) {
    return <div className={styles.centeredMessageContainer}><p className={styles.errorMessage}>{error}</p></div>;
  }

  if (tracks.length === 0) {
    return <div className={styles.centeredMessageContainer}><p className={styles.emptyState}>No career tracks recommended yet. Please complete the quiz.</p></div>;
  }

  return (
    <div className={styles.careerTracksContainer}>
      <h2 className={styles.pageTitle}>Recommended Career Tracks 🎯</h2>
      <div className={styles.tracksGrid}>
        {tracks.map((track) => (
          <div key={track._id || track.title} className={styles.trackCard}>
            <div className={styles.cardContent}>
              <h3 className={styles.cardTitle}>{track.title}</h3>
              <p className={styles.cardText}><strong>Avg. Salary:</strong> {track.avgSalary}</p>
              <p className={styles.cardText}><strong>Key Skills:</strong> {track.skills.join(', ')}</p>
              <p className={styles.cardText}><strong>Essential Tools:</strong> {track.tools.join(', ')}</p>
              <p className={styles.cardText}><strong>Growth Path:</strong> {track.growth}</p>
            </div>
            <button onClick={() => handleViewRoadmap(track._id)} className={styles.viewRoadmapButton}>
              View Roadmap
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CareerTracks;