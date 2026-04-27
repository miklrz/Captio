/* ПР №1 и №2: Главный компонент приложения */
import React, { useState } from 'react';

/* ПР №2: Импорт компонентов из отдельных файлов */
import Header from './components/Header';
import UploadForm from './components/UploadForm';
import SubtitleResult from './components/SubtitleResult';
import Loader from './components/Loader';

import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="app">
      {/* ПР №2: Используем компонент как тег */}
      <Header />

      <main className="main">
        {/* Hero секция */}
        <section className="hero">
          <span className="heroTag">AI Subtitle Generator</span>
          <h1 className="heroTitle">
            Субтитры за&nbsp;
            <span className="heroAccent">минуты</span>
          </h1>
          <p className="heroSub">
            Загрузите видео с Яндекс Диска — Whisper распознает речь
            и сформирует субтитры с таймкодами.
          </p>
        </section>

        {/* Форма загрузки */}
        <UploadForm onResult={setResult} onLoading={setLoading} />

        {/* Индикатор обработки */}
        {loading && <Loader />}

        {/* Результат */}
        {result && !loading && <SubtitleResult result={result} />}
      </main>

      <footer className="footer">
        <span>SubGen © 2026</span>
        <span>Powered by OpenAI Whisper</span>
      </footer>
    </div>
  );
}

export default App;
