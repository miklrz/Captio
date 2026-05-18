import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchTasks, addTask, toggleTask, deleteTask } from '../redux/tasksSlice';
import classes from './Agreement.module.css';

function Tasks() {
  const dispatch = useDispatch();
  const { list, loading, error } = useSelector(state => state.tasks);
  const { user } = useSelector(state => state.auth);
  const [input, setInput] = useState('');

  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    dispatch(fetchTasks());
  }, [dispatch]);

  const handleAdd = () => {
    if (!input.trim()) return;
    dispatch(addTask(input.trim()));
    setInput('');
  };

  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>07</span>
        <span>Задачи (CRUD + PostgreSQL + Роли)</span>
      </div>

      <div className={classes.card}>
        {/* Информация о роли */}
        <div style={{ marginBottom: '16px', padding: '12px', background: '#f0f0f0', borderRadius: '8px' }}>
          <p style={{ margin: 0, fontSize: '14px', color: '#555' }}>
            <strong>Ваша роль:</strong> {isAdmin ? '🔑 Администратор' : '👤 Пользователь'}
          </p>
          <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#888' }}>
            {isAdmin 
              ? 'Вы можете видеть, редактировать и удалять задачи всех пользователей'
              : 'Вы можете создавать, редактировать и удалять только свои задачи'
            }
          </p>
        </div>

        {/* CREATE */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
          <input
            style={{
              flex: 1,
              padding: '12px 14px',
              border: '1px solid #e0e0e0',
              borderRadius: '10px',
              fontSize: '14px',
              outline: 'none',
            }}
            placeholder="Новая задача..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAdd()}
          />
          <button
            onClick={handleAdd}
            style={{
              padding: '12px 20px',
              background: '#c8ff00',
              border: 'none',
              borderRadius: '10px',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Добавить
          </button>
        </div>

        {/* Ошибки */}
        {error && (
          <p style={{ color: '#ff4444', fontSize: '14px', marginBottom: '12px' }}>
            Ошибка: {error}
          </p>
        )}

        {/* READ */}
        {loading && <p style={{ color: '#888', fontSize: '14px' }}>Загрузка...</p>}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {list.map(task => (
            <div
              key={task.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                background: '#f9f9f6',
                border: '1px solid #e8e8e8',
                borderRadius: '10px',
              }}
            >
              {/* UPDATE */}
              <input
                type="checkbox"
                checked={task.done}
                onChange={() => dispatch(toggleTask({ id: task.id, done: !task.done }))}
                style={{
                  width: '16px',
                  height: '16px',
                  accentColor: '#c8ff00',
                  cursor: 'pointer',
                }}
              />
              <div style={{ flex: 1 }}>
                <span
                  style={{
                    fontSize: '14px',
                    textDecoration: task.done ? 'line-through' : 'none',
                    color: task.done ? '#aaa' : '#111',
                    display: 'block',
                  }}
                >
                  {task.title}
                </span>
                {/* Для админа показываем владельца задачи */}
                {isAdmin && task.owner_name && (
                  <span style={{ fontSize: '12px', color: '#888', marginTop: '4px', display: 'block' }}>
                    Владелец: {task.owner_name} ({task.owner_login})
                  </span>
                )}
              </div>
              {/* DELETE */}
              <button
                onClick={() => dispatch(deleteTask(task.id))}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#ccc',
                  fontSize: '18px',
                  cursor: 'pointer',
                  lineHeight: 1,
                }}
              >
                ×
              </button>
            </div>
          ))}

          {!loading && list.length === 0 && (
            <p
              style={{
                color: '#aaa',
                fontSize: '14px',
                textAlign: 'center',
                padding: '20px',
              }}
            >
              Задач пока нет. Добавьте первую!
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

export default Tasks;