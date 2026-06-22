import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import classes from '../components/SubtitleResult.module.css'; // Переиспользуем стили
import { apiUrl, VIDEOS_API } from '../config';

const API = VIDEOS_API;

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const formatDate = (value) => {
  if (!value) return 'Дата неизвестна';
  return new Date(value).toLocaleString('ru-RU');
};

function History() {
  const { id } = useParams(); // ПР №4: Получение динамического параметра из URL
  const [items, setItems] = useState([]);
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    const url = id ? `${API}/${id}` : `${API}/history`;

    fetch(url, { headers: getHeaders() })
      .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(data.detail || data.message || 'Ошибка загрузки истории');
        }
        return data;
      })
      .then((data) => {
        if (id) setItem(data);
        else setItems(data);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  // Если ID в URL есть, показываем "детали", иначе список
  if (id) {
    return (
      <div style={{ padding: '20px' }}>
        <Link to="/history">← Назад к истории</Link>
        {loading && <p>Загрузка...</p>}
        {error && <p style={{ color: '#ff4444' }}>{error}</p>}
        {item && (
          <>
            <h2>Обработка #{item.id}</h2>
            <p>Статус: {item.status}</p>
            <p>Источник: {item.source_url}</p>
            <p>Дата: {formatDate(item.created_at)}</p>
            {item.srt_url && (
              <p>
                <a href={apiUrl(item.srt_url)}>Скачать .srt</a>
              </p>
            )}
            <p style={{ whiteSpace: 'pre-wrap' }}>{item.text || 'Текст ещё не создан'}</p>
          </>
        )}
      </div>
    );
  }

  return (
    <section className={classes.section}>
      <div className={classes.label}>
        <span className={classes.labelNum}>03</span>
        <span>История запросов</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '20px' }}>
        {loading && <p>Загрузка...</p>}
        {error && <p style={{ color: '#ff4444' }}>{error}</p>}
        {!loading && !error && items.length === 0 && (
          <p style={{ color: '#888' }}>История пока пустая.</p>
        )}
        {items.map((item) => (
          <Link 
            key={item.id} 
            to={`/history/${item.id}`} 
            style={{ 
              padding: '15px', 
              background: '#1a1a1a', 
              borderRadius: '8px',
              textDecoration: 'none',
              color: 'white',
              border: '1px solid #333'
            }}
          >
            <strong>Обработка #{item.id}</strong> — {item.status} — {formatDate(item.created_at)}
          </Link>
        ))}
      </div>
    </section>
  );
}

export default History;
