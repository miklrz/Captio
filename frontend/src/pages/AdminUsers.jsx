import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import classes from './Login.module.css';

const API = 'http://localhost:4000/api/auth';

function AdminUsers() {
  const navigate = useNavigate();
  const { user, token } = useSelector(state => state.auth);

  const [users, setUsers]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [saved, setSaved]     = useState(null); // id последнего сохранённого

  // Защита — только админ
  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    if (!user.roles.includes('admin')) { navigate('/'); return; }

    fetch(`${API}/users`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(data => { setUsers(data); setLoading(false); })
      .catch(() => { setError('Ошибка загрузки'); setLoading(false); });
  }, []);

  const handleRoleToggle = async (targetUser, role) => {
    const hasRole    = targetUser.roles.includes(role);
    const newRoles   = hasRole
      ? targetUser.roles.filter(r => r !== role)   // убрать роль
      : [...targetUser.roles, role];                // добавить роль

    // Нельзя оставить пользователя совсем без ролей
    if (newRoles.length === 0) return;

    const res = await fetch(`${API}/users/${targetUser.id}/role`, {
      method:  'PATCH',
      headers: {
        'Content-Type':  'application/json',
        Authorization:   `Bearer ${token}`,
      },
      body: JSON.stringify({ roles: newRoles }),
    });

    if (res.ok) {
      const updated = await res.json();
      setUsers(prev => prev.map(u => u.id === updated.id ? updated : u));
      setSaved(updated.id);
      setTimeout(() => setSaved(null), 2000);
    }
  };

  if (loading) return <p style={{ padding: '20px', color: '#888' }}>Загрузка...</p>;
  if (error)   return <p style={{ padding: '20px', color: '#e53e3e' }}>{error}</p>;

  const ALL_ROLES = ['user', 'admin'];

  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>06</span>
        <span>Управление пользователями</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {users.map(u => (
          <div key={u.id} style={{
            background: '#fff',
            border: `1px solid ${saved === u.id ? '#c8ff00' : '#e8e8e8'}`,
            borderRadius: '12px',
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            transition: 'border-color 0.3s',
          }}>
            {/* Аватар */}
            <div style={{
              width: '40px', height: '40px', borderRadius: '50%',
              background: '#f0f0f0', display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: '18px', flexShrink: 0,
            }}>
              {u.name[0]}
            </div>

            {/* Имя и логин */}
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: '15px', color: '#111' }}>{u.name}</div>
              <div style={{ fontSize: '12px', color: '#888' }}>@{u.login}</div>
            </div>

            {/* Роли — кликабельные теги */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {ALL_ROLES.map(role => {
                const active = u.roles.includes(role);
                // Нельзя снять единственную роль
                const disabled = active && u.roles.length === 1;
                // Нельзя менять роли самому себе
                const isSelf = u.id === user.id;

                return (
                  <button
                    key={role}
                    disabled={disabled || isSelf}
                    onClick={() => handleRoleToggle(u, role)}
                    title={isSelf ? 'Нельзя менять свои роли' : disabled ? 'Минимум одна роль' : ''}
                    style={{
                      padding: '5px 12px',
                      borderRadius: '20px',
                      border: 'none',
                      fontSize: '12px',
                      fontWeight: 700,
                      cursor: (disabled || isSelf) ? 'not-allowed' : 'pointer',
                      transition: 'all 0.15s',
                      background: active
                        ? (role === 'admin' ? '#1a1a1a' : '#c8ff00')
                        : '#f0f0f0',
                      color: active
                        ? (role === 'admin' ? '#c8ff00' : '#1a1a1a')
                        : '#aaa',
                      opacity: (disabled || isSelf) ? 0.5 : 1,
                    }}
                  >
                    {active ? '✓ ' : '+ '}{role}
                  </button>
                );
              })}
            </div>

            {/* Индикатор сохранения */}
            {saved === u.id && (
              <span style={{ fontSize: '12px', color: '#666', whiteSpace: 'nowrap' }}>
                Сохранено ✓
              </span>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

export default AdminUsers;