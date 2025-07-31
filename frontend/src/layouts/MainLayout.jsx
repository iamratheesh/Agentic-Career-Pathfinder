import React from 'react';
import { Link } from 'react-router-dom';
import styles from './MainLayout.module.css';

const MainLayout = ({ children }) => {
  return (
    <div className={styles.layoutContainer}>
      <header className={styles.header}>
        <nav className={styles.nav}>
          <Link to="/" className={styles.logo}>Career Pathfinder</Link>
          <div className={styles.navLinks}>
            <Link to="/all-sessions" className={styles.navLink}>All Learning</Link>
          </div>
        </nav>
      </header>

      <main className={styles.mainContent}>
        {children}
      </main>
      
      <footer className={styles.footer}>
        <p>&copy; {new Date().getFullYear()} Agentic Career Pathfinder</p>
      </footer>
    </div>
  );
};

export default MainLayout;