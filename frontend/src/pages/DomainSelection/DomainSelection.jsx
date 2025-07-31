// frontend/src/pages/DomainSelection/DomainSelection.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { initDomain } from '../../api/api';
import { useSession } from '../../hooks/useSession';
import styles from './DomainSelection.module.css';
import Loader from '../../components/Loader/Loader';


const DomainSelection = () => {
  const [domain, setDomain] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { saveSessionId, clearSessionId } = useSession();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return; // Prevent multiple submissions
    
    setLoading(true);
    setError(null);
    clearSessionId(); // Clear any old session before starting a new one

    try {
      const response = await initDomain(domain);
      saveSessionId(response.sessionId); // Save the new session ID
      navigate('/quiz', { state: { quizId: response.quizId, questions: response.questions } });
    } catch (err) {
      console.error('Error initiating domain:', err);
      setError('Failed to start session. Please try again. ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2 className={styles.title}>Start Your Career Journey 🚀</h2>
        <p className={styles.description}>
          Enter your area of interest to begin your personalized career guidance.
        </p>

        <form onSubmit={handleSubmit}>
          <div className={styles.textInputWrapper}>
            <label htmlFor="domain" className={styles.label}>Domain of Interest</label>
            <input
              type="text"
              id="domain"
              className={styles.input}
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="e.g., Frontend Developer, Data Scientist"
              required
              autoFocus
            />
          </div>

          {error && (
            <div className={styles.alert}>
              <strong>Error:</strong> {error}
            </div>
          )}

          <button type="submit" className={styles.button} disabled={loading}>
            {loading && <Loader />}
            <span>{loading ? 'Starting...' : 'Start Guidance'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default DomainSelection;