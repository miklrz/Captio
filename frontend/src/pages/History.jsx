import React from 'react';
import { useParams, Link } from 'react-router-dom';
import classes from '../components/SubtitleResult.module.css'; // Переиспользуем стили

const MOCK_HISTORY = [
  { id: '1', name: 'Интервью с инженером.mp4', date: '20.04.2026' },
  { id: '2', name: 'Лекция по ML.mp4', date: '21.04.2026' },
  { id: '3', name: 'Таймлапс разработки.mov', date: '22.04.2026' },
];

function History() {
  const { id } = useParams(); // ПР №4: Получение динамического параметра из URL

  // Если ID в URL есть, показываем "детали", иначе список
  if (id) {
    const item = MOCK_HISTORY.find(h => h.id === id);
    return (
      <div style={{ padding: '20px' }}>
        <Link to="/history">← Назад к истории</Link>
        <h2>Детали записи: {item?.name}</h2>
        <p>Здесь мог бы быть текст субтитров для ID: {id}</p>
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
        {MOCK_HISTORY.map((item) => (
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
            <strong>{item.name}</strong> — {item.date}
          </Link>
        ))}
      </div>
    </section>
  );
}

export default History;