import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logout } from '../redux/authSlice';
import classes from './Login.module.css'; // переиспользуем стили
import { Link } from 'react-router-dom';


// Функции авторизации из методички
const hasRole   = (user, roles)  => roles.some(r => user.roles.includes(r));
const isAllowed = (user, rights) => rights.some(r => user.rights.includes(r));

function Profile() {
  const dispatch  = useDispatch();
  const navigate  = useNavigate();
  const user      = useSelector(state => state.auth.user);

  if (!user) {
    navigate('/login');
    return null;
  }

  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>06</span>
        <span>Профиль</span>
      </div>

      <div className={classes.card} style={{ maxWidth: '100%' }}>
        <h2 className={classes.title}>Привет, {user.name}!</h2>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {user.roles.map(role => (
            <span key={role} style={{
              background: role === 'admin' ? '#1a1a1a' : '#ebebeb',
              color: role === 'admin' ? '#c8ff00' : '#555',
              padding: '4px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: 700
            }}>
              {role}
            </span>
          ))}
        </div>

        {/* Контент для всех авторизованных пользователей */}
        {isAllowed(user, ['can_view_articles']) && (
          <div style={{ padding: '16px', background: '#f9f9f6', borderRadius: '10px' }}>
            <strong>Доступно вам:</strong> просмотр субтитров и истории запросов.
          </div>
        )}

        {/* Контент только для администратора */}
        {hasRole(user, ['admin']) && (
        <div style={{ padding: '16px', background: '#fff9e6', border: '1px solid #f0e0a0', borderRadius: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong>Панель администратора</strong>
            <Link to="/admin/users" style={{
            padding: '8px 16px', background: '#1a1a1a', color: '#c8ff00',
            borderRadius: '8px', fontSize: '13px', fontWeight: 700, textDecoration: 'none'
            }}>
            Управление пользователями →
            </Link>
        </div>
        )}

        <button
          className={classes.btn}
          onClick={() => { dispatch(logout()); navigate('/login'); }}
        >
          Выйти
        </button>
      </div>
    </section>
  );
}

export default Profile;