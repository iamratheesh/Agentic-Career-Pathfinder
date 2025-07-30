// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import DomainSelection from './pages/DomainSelection/DomainSelection';
import Quiz from './pages/Quiz/Quiz';
import CareerTracks from './pages/CareerTracks/CareerTracks';
import Roadmap from './pages/Roadmap/Roadmap';
import Tracker from './pages/Tracker/Tracker';
import SessionSummary from './pages/SessionSummary/SessionSummary';
import AllSessions from './pages/AllSessions/AllSessions'; // NEW: Import AllSessions
import NotFound from './pages/NotFound/NotFound';

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<DomainSelection />} />
          <Route path="/quiz" element={<Quiz />} />
          <Route path="/career-tracks" element={<CareerTracks />} />
          <Route path="/roadmap/:trackId" element={<Roadmap />} />
          <Route path="/tracker" element={<Tracker />} />
          <Route path="/session-summary/:sessionId?" element={<SessionSummary />} />
          <Route path="/all-sessions" element={<AllSessions />} /> {/* NEW: Add route for all sessions */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;