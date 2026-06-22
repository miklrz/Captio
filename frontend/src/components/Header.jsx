import React from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import classes from './Header.module.css';

function Header() {
  const user = useSelector((state) => state.auth.user);
  const isAdmin = user?.role === 'admin';

  return (
    <header className={classes.header}>
      <div className={classes.logo}>
        <Link to="/" className={classes.logoLink}>
          <span className={classes.logoIcon}>C</span>
          <span className={classes.logoText}>Captio</span>
        </Link>
      </div>
      <nav className={classes.nav}>
        <Link to="/" className={classes.navLink}>Главная</Link>
        <Link to="/history" className={classes.navLink}>История</Link>
        <Link to="/about" className={classes.navLink}>О сервисе</Link>
        {isAdmin && <Link to="/admin/users" className={classes.navLink}>Пользователи</Link>}
        {user
          ? <Link to="/profile" className={classes.navLink}>{user.name}</Link>
          : <Link to="/login" className={classes.navLink}>Войти</Link>
          }
          <Link to="/tasks" className={classes.navLink}>Задачи</Link>
      </nav>
    </header>
  );
}

export default Header;
