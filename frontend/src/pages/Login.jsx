import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../redux/authSlice';
import classes from './Login.module.css';

function Login() {
  const dispatch  = useDispatch();
  const navigate  = useNavigate();
  const { loading, error } = useSelector(state => state.auth);

  const [form, setForm] = useState({ login: '', password: '' });

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async () => {
    const result = await dispatch(loginUser(form));
    if (loginUser.fulfilled.match(result)) {
      navigate('/profile'); // после входа — на профиль
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSubmit();
  };

  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>06</span>
        <span>Вход в систему</span>
      </div>

      <div className={classes.card}>
        <h2 className={classes.title}>Авторизация</h2>
        <p className={classes.hint}>
          Тест: <b>paimon / 123456</b> (роль: user) или <b>admin / admin123</b> (роль: admin)
        </p>

        <div className={classes.field}>
          <label className={classes.label}>Логин</label>
          <input
            className={classes.input}
            name="login"
            value={form.login}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="paimon"
          />
        </div>

        <div className={classes.field}>
          <label className={classes.label}>Пароль</label>
          <input
            className={classes.input}
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="••••••"
          />
        </div>

        {error && <p className={classes.error}>{error}</p>}

        <button
          className={classes.btn}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? 'Входим...' : 'Войти'}
        </button>
      </div>
    </section>
  );
}

export default Login;