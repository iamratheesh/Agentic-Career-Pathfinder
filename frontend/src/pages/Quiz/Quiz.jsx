import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { submitAnswers } from '../../api/api';
import { useSession } from '../../hooks/useSession';
import styles from './Quiz.module.css';
import Loader from '../../components/Loader/Loader';



const Quiz = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { sessionId } = useSession();

  const [questions, setQuestions] = useState([]);
  const [currentAnswers, setCurrentAnswers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (location.state?.questions && location.state?.quizId) {
      setQuestions(location.state.questions);
      setCurrentAnswers(Array(location.state.questions.length).fill(''));
    } 
  }, [location.state, navigate]);

  const handleAnswerChange = (index, value) => {
    const newAnswers = [...currentAnswers];
    newAnswers[index] = value;
    setCurrentAnswers(newAnswers);
  };

  const handleSubmitQuiz = async () => {
    if (!sessionId) {
      setError("Session not found. Please start from the Domain Selection.");
      return;
    }

    if (currentAnswers.some(answer => answer.trim() === '')) {
      setError("Please answer all questions before submitting.");
      return;
    }

    setLoading(true);
    setError(null);

    const answersPayload = questions.map((q, index) => ({
      question: q.question,
      answer: currentAnswers[index],
    }));

    try {
      const response = await submitAnswers(sessionId, location.state.quizId, answersPayload);
      if (response.level && response.nextStep === "career-track-recommendation") {
        navigate('/career-tracks', { state: { level: response.level } });
      } else {
        setError("Quiz submission failed or level not determined.");
      }
    } catch (err) {
      console.error('Error submitting answers:', err);
      setError('Failed to submit quiz. Please try again. ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  if (questions.length === 0) {
    return <p className={styles.emptyState}>No quiz questions found. Please return to the homepage to start a new session.</p>;
  }

  return (
    <div className={styles.quizContainer}>
      <div className={styles.card}>
        <h2 className={styles.title}>Skill Assessment Quiz</h2>
        <p className={styles.instructions}>
          Please answer the following questions based on your knowledge. Your answers will help us determine your skill level.
        </p>
        <div className={styles.questionsList}>
          {questions.map((q, index) => (
            <div key={q.id || index} className={styles.questionItem}>
              <label htmlFor={`question-${index}`} className={styles.questionText}>
                <strong>{index + 1}.</strong> {q.question}
              </label>
              <textarea
                id={`question-${index}`}
                value={currentAnswers[index]}
                onChange={(e) => handleAnswerChange(index, e.target.value)}
                placeholder="Type your answer here..."
                rows="4"
                className={styles.answerInput}
                required
              />
            </div>
          ))}
        </div>

        {error && <div className={styles.errorText}>{error}</div>}

        <button onClick={handleSubmitQuiz} disabled={loading} className={styles.submitButton}>
          {loading && <Loader />}
          <span>{loading ? 'Submitting...' : 'Submit Quiz'}</span>
        </button>
      </div>
    </div>
  );
};

export default Quiz;