/* ПР №2: Компонент формы загрузки */
import React, { useState } from 'react';
import classes from './UploadForm.module.css';

function UploadForm({ onResult, onLoading }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim()) {
      setError('Введите ссылку на Яндекс Диск');
      return;
    }
    setError('');
    onLoading(true);

    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;

    fetch('http://localhost:8000/upload-video', {
      method: 'POST',
      headers,
      body: JSON.stringify({ video_url: url }),
    })
      .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(data.detail || data.message || `Ошибка сервера: ${res.status}`);
        }
        return data;
      })
      .then((data) => {
        onResult(data);
        onLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        onLoading(false);
      });
  }

  return (
    <section className={classes.section} id="upload">
      <div className={classes.label}>
        <span className={classes.labelNum}>01</span>
        <span>Ссылка на видео</span>
      </div>
      <form className={classes.form} onSubmit={handleSubmit}>
        <div className={classes.inputWrap}>
          <span className={classes.inputPrefix}>ЯД →</span>
          <input
            className={classes.input}
            type="text"
            placeholder="https://disk.yandex.ru/d/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </div>
        {error && <p className={classes.error}>{error}</p>}
        <button className={classes.button} type="submit">
          <span>Генерировать субтитры</span>
          <span className={classes.buttonArrow}>→</span>
        </button>
      </form>
    </section>
  );
}

export default UploadForm;
