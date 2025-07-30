// frontend/src/hooks/useSession.js
import { useState, useEffect } from 'react';

const SESSION_KEY = 'careerPathfinderSessionId';

export const useSession = () => {
  const [sessionId, setSessionId] = useState(() => {
    // Initialize from localStorage
    return localStorage.getItem(SESSION_KEY) || null;
  });

  const saveSessionId = (id) => {
    setSessionId(id);
    localStorage.setItem(SESSION_KEY, id);
  };

  const clearSessionId = () => {
    setSessionId(null);
    localStorage.removeItem(SESSION_KEY);
  };

  return { sessionId, saveSessionId, clearSessionId };
};