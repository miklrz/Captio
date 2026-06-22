import React, { useEffect, useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { checkAuth } from './redux/authSlice';
import Header from './components/Header';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import History from './pages/History';
import About from './pages/About';
import Login from './pages/Login';
import Profile from './pages/Profile';
import AdminUsers from './pages/AdminUsers';
import Status from './pages/Status';
import { getUiLanguage } from './i18n';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uiLanguage, setUiLanguage] = useState(getUiLanguage());
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(checkAuth());
  }, [dispatch]);

  return (
    <div className="app">
      <Header />

      <main className="main">
        <Routes>
          <Route
            path="/"
            element={
              <Home
                result={result}
                setResult={setResult}
                loading={loading}
                setLoading={setLoading}
                uiLanguage={uiLanguage}
                setUiLanguage={setUiLanguage}
              />
            }
          />

          <Route path="/status/:id" element={<Status uiLanguage={uiLanguage} />} />
          <Route path="/history" element={<History />} />
          <Route path="/history/:id" element={<History />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/users"
            element={
              <ProtectedRoute requireAdmin>
                <AdminUsers />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <footer className="footer">
        <span>Captio © 2026</span>
        <span>Powered by OpenAI Whisper</span>
      </footer>
    </div>
  );
}

export default App;
