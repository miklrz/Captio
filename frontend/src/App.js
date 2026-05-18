import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { checkAuth } from './redux/authSlice';
import Header from './components/Header';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import History from './pages/History';
import Dialogs from './pages/Dialogs';
import './App.css';
import Agreement from './pages/Agreement';
import Login from './pages/Login';
import Profile from './pages/Profile';
import Tasks from './pages/Tasks';
import AdminUsers from './pages/AdminUsers';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();

  // Проверяем токен при загрузке приложения
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
              />
            }
          />

          <Route path="/history" element={<History />} />
          <Route path="/history/:id" element={<History />} />

          <Route path="/dialogs" element={<Dialogs />} />
          <Route path="/dialogs/:id" element={<Dialogs />} />

          <Route
            path="/about"
            element={
              <div style={{ color: 'white', padding: '20px' }}>
                Сервис для автоматической генерации субтитров.
              </div>
            }
          />
          <Route path="/agreement" element={<Agreement />} />

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
            path="/tasks"
            element={
              <ProtectedRoute>
                <Tasks />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/users"
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminUsers />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>

      <footer className="footer">
        <span>SubGen © 2026</span>
        <span>Powered by OpenAI Whisper</span>
      </footer>
    </div>
  );
}

export default App;