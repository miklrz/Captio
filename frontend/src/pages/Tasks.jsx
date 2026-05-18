import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchTasks, addTask, toggleTask, deleteTask } from '../redux/tasksSlice';
import classes from './Agreement.module.css'; // переиспользуем стили карточки

function Tasks() {
  const dispatch = useDispatch();
  const { list, loading } = useSelector(state => state.tasks);
  const [input, setInput] = useState('');

  // READ — загружаем при открытии страницы
  useEffect(() => {
    dispatch(fetchTasks());
  }, [dispatch]);

  // CREATE
  const handleAdd = () => {
    if (!input.trim()) return;
    dispatch(addTask(input.trim()));
    setInput('');
  };

  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>07</span>
        <span>Задачи (CRUD + PostgreSQL)</span>
      </div>

      <div className={classes.card}>
        {/* CREATE */}
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            style={{ flex: 1, padding: '12px 14px', border: '1px solid #e0e0e0', borderRadius: '10px', fontSize: '14px', outline: 'none' }}
            placeholder="Новая задача..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAdd()}
          />
          <button
            onClick={handleAdd}
            style={{ padding: '12px 20px', background: '#c8ff00', border: 'none', borderRadius: '10px', fontWeight: 700, cursor: 'pointer' }}
          >
            Добавить
          </button>
        </div>

        {/* READ */}
        {loading && <p style={{ color: '#888', fontSize: '14px' }}>Загрузка...</p>}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {list.map(task => (
            <div key={task.id} style={{
              display: 'flex', alignItems: 'center', gap: '12px',
              padding: '12px 16px', background: '#f9f9f6',
              border: '1px solid #e8e8e8', borderRadius: '10px'
            }}>
              {/* UPDATE */}
              <input
                type="checkbox"
                checked={task.done}
                onChange={() => dispatch(toggleTask({ id: task.id, done: !task.done }))}
                style={{ width: '16px', height: '16px', accentColor: '#c8ff00', cursor: 'pointer' }}
              />
              <span style={{
                flex: 1, fontSize: '14px',
                textDecoration: task.done ? 'line-through' : 'none',
                color: task.done ? '#aaa' : '#111'
              }}>
                {task.title}
              </span>
              {/* DELETE */}
              <button
                onClick={() => dispatch(deleteTask(task.id))}
                style={{ background: 'none', border: 'none', color: '#ccc', fontSize: '18px', cursor: 'pointer', lineHeight: 1 }}
              >
                ×
              </button>
            </div>
          ))}

          {!loading && list.length === 0 && (
            <p style={{ color: '#aaa', fontSize: '14px', textAlign: 'center', padding: '20px' }}>
              Задач пока нет. Добавьте первую!
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

export default Tasks;