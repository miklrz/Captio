import React from 'react';
/* ПР №2: Импорт компонентов из папки уровнем выше */
import Header from '../components/Header';
import UploadForm from '../components/UploadForm';
import SubtitleResult from '../components/SubtitleResult';
import Loader from '../components/Loader';

function Home({ result, setResult, loading, setLoading }) {
  return (
    <>
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
    </>
  );
}

export default Home;