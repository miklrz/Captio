import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home'; // Проверьте этот импорт
import History from './pages/History';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="app">
      <Header />
      
      <main className="main">
        <Routes>
          {/* Главная страница (ПР №3) */}
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
          
          {/* История и динамические пути (ПР №4) */}
          <Route path="/history" element={<History />} />
          <Route path="/history/:id" element={<History />} />
          
          {/* Страница-заглушка "О сервисе" */}
          <Route path="/about" element={<div style={{color: 'white', padding: '20px'}}>Сервис для автоматической генерации субтитров.</div>} />
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