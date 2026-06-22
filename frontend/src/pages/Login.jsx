import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { clearAuthError, loginUser, registerUser } from '../redux/authSlice';
import classes from './Login.module.css';

function Login() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state) => state.auth);

  const [mode, setMode] = useState('login');
  const [localError, setLocalError] = useState('');
  const [form, setForm] = useState({
    name: '',
    login: '',
    password: '',
    confirmPassword: '',
  });

  const isRegister = mode === 'register';

  const handleChange = (e) => {
    setLocalError('');
    dispatch(clearAuthError());
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setLocalError('');
    dispatch(clearAuthError());
  };

  const validate = () => {
    if (isRegister && !form.name.trim()) return 'Введите имя';
    if (!form.login.trim()) return 'Введите логин';
    if (!form.password) return 'Введите пароль';
    if (isRegister && form.password.length < 4) return 'Пароль должен быть не короче 4 символов';
    if (isRegister && form.password !== form.confirmPassword) return 'Пароли не совпадают';
    return '';
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    const validationError = validate();
    if (validationError) {
      setLocalError(validationError);
      return;
    }

    const action = isRegister ? registerUser : loginUser;
    const payload = isRegister
      ? { name: form.name, login: form.login, password: form.password }
      : { login: form.login, password: form.password };
    const result = await dispatch(action(payload));

    if (action.fulfilled.match(result)) {
      navigate('/profile');
    }
  };

  const visibleError = localError || error;

  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>04</span>
        <span>{isRegister ? 'Регистрация' : 'Вход в систему'}</span>
      </div>

      <form className={classes.card} onSubmit={handleSubmit}>
        <div className={classes.tabs} role="tablist" aria-label="Авторизация">
          <button
            type="button"
            className={mode === 'login' ? classes.activeTab : classes.tab}
            onClick={() => switchMode('login')}
          >
            Вход
          </button>
          <button
            type="button"
            className={mode === 'register' ? classes.activeTab : classes.tab}
            onClick={() => switchMode('register')}
          >
            Регистрация
          </button>
        </div>

        <h2 className={classes.title}>{isRegister ? 'Создать аккаунт' : 'Авторизация'}</h2>
        <p className={classes.hint}>
          {isRegister
            ? 'Новый пользователь создается с ролью user. Роль admin назначается только администратором.'
            : 'Тестовый вход: paimon / 123456 или admin / admin123.'}
        </p>

        {isRegister && (
          <div className={classes.field}>
            <label className={classes.label} htmlFor="name">Имя</label>
            <input
              id="name"
              className={classes.input}
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Михаил"
              autoComplete="name"
            />
          </div>
        )}

        <div className={classes.field}>
          <label className={classes.label} htmlFor="login">Логин</label>
          <input
            id="login"
            className={classes.input}
            name="login"
            value={form.login}
            onChange={handleChange}
            placeholder="paimon"
            autoComplete="username"
          />
        </div>

        <div className={classes.field}>
          <label className={classes.label} htmlFor="password">Пароль</label>
          <input
            id="password"
            className={classes.input}
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            placeholder="••••••"
            autoComplete={isRegister ? 'new-password' : 'current-password'}
          />
        </div>

        {isRegister && (
          <div className={classes.field}>
            <label className={classes.label} htmlFor="confirmPassword">Повторите пароль</label>
            <input
              id="confirmPassword"
              className={classes.input}
              name="confirmPassword"
              type="password"
              value={form.confirmPassword}
              onChange={handleChange}
              placeholder="••••••"
              autoComplete="new-password"
            />
          </div>
        )}

        {visibleError && <p className={classes.error}>{visibleError}</p>}

        <button className={classes.btn} type="submit" disabled={loading}>
          {loading ? 'Отправляем...' : isRegister ? 'Зарегистрироваться' : 'Войти'}
        </button>
      </form>
    </section>
  );
}

export default Login;
