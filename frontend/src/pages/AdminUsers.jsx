import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { fetchUsers, updateUserRole, deleteUser } from '../redux/authSlice';
import classes from './Agreement.module.css';

function AdminUsers() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, users } = useSelector(state => state.auth);

  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    // Если не админ — редирект
    if (!isAdmin) {
      navigate('/');
      return;
    }
    dispatch(fetchUsers());
  }, [dispatch, isAdmin, navigate]);

  const handleRoleChange = (userId, currentRole) => {
    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    if (window.confirm(`Изменить роль на "${newRole}"?`)) {
      dispatch(updateUserRole({ userId, role: newRole }));
    }
  };

  const handleDelete = (userId, userName) => {
    if (window.confirm(`Удалить пользователя "${userName}"?`)) {
      dispatch(deleteUser(userId));
    }
  };

  if (!isAdmin) return null;

  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>08</span>
        <span>Управление пользователями (Админ)</span>
      </div>

      <div className={classes.card}>
        <h3 style={{ margin: '0 0 16px', fontSize: '18px', fontWeight: 600 }}>
          Список пользователей
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {users.map(u => (
            <div
              key={u.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '16px',
                background: '#f9f9f6',
                border: '1px solid #e8e8e8',
                borderRadius: '10px',
              }}
            >
              <div style={{ flex: 1 }}>
                <p style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#111' }}>
                  {u.name}
                </p>
                <p style={{ margin: '4px 0 0', fontSize: '14px', color: '#666' }}>
                  Логин: {u.login}
                </p>
                <p style={{ margin: '4px 0 0', fontSize: '14px', color: '#666' }}>
                  ID: {u.id}
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {/* Роль */}
                <span
                  style={{
                    padding: '6px 12px',
                    background: u.role === 'admin' ? '#ff9800' : '#4caf50',
                    color: 'white',
                    borderRadius: '6px',
                    fontSize: '13px',
                    fontWeight: 600,
                  }}
                >
                  {u.role === 'admin' ? '🔑 Админ' : '👤 Пользователь'}
                </span>

                {/* Кнопка изменения роли */}
                {u.id !== user.id && (
                  <>
                    <button
                      onClick={() => handleRoleChange(u.id, u.role)}
                      style={{
                        padding: '8px 16px',
                        background: '#2196F3',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '13px',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Изменить роль
                    </button>

                    {/* Кнопка удаления */}
                    <button
                      onClick={() => handleDelete(u.id, u.name)}
                      style={{
                        padding: '8px 16px',
                        background: '#f44336',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '13px',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Удалить
                    </button>
                  </>
                )}

                {u.id === user.id && (
                  <span style={{ fontSize: '13px', color: '#888', fontStyle: 'italic' }}>
                    (Это вы)
                  </span>
                )}
              </div>
            </div>
          ))}

          {users.length === 0 && (
            <p style={{ color: '#aaa', fontSize: '14px', textAlign: 'center', padding: '20px' }}>
              Пользователей не найдено
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

export default AdminUsers;