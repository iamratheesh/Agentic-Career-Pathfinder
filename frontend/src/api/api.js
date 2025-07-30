// frontend/src/api/api.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const initDomain = async (domain) => {
  const response = await api.post('/init-domain', { domain });
  return response.data;
};

export const submitAnswers = async (sessionId, quizId, answers) => {
  const response = await api.post('/submit-answers', { sessionId, quizId, answers });
  return response.data;
};

export const getCareerTracks = async (sessionId) => {
  const response = await api.get(`/career-tracks/${sessionId}`);
  return response.data;
};

export const getRoadmap = async (trackId) => {
  const response = await api.get(`/roadmap/${trackId}`);
  return response.data;
};

export const getSessionSummary = async (sessionId) => {
  const response = await api.get(`/session-summary/${sessionId}`);
  return response.data;
};

export const getSessionDetails = async (sessionId) => {
  const response = await api.get(`/session/${sessionId}`);
  return response.data;
};

// NEW: API call to get all sessions
export const getAllSessions = async () => {
    const response = await api.get('/sessions');
    return response.data;
};

export const updateTaskStatus = async (sessionId, taskUpdateData) => {
  const response = await api.patch(`/tracker/${sessionId}`, taskUpdateData);
  return response.data;
};