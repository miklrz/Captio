import React from 'react';
import { Link } from 'react-router-dom';
import classes from './Header.module.css';
import { useSelector } from 'react-redux';

function Header() {
  const user = useSelector(state => state.auth.user);
  return (
    <header className={classes.header}>
      <div className={classes.logo}>
        <Link to="/" className={classes.logoLink}>
          <span className={classes.logoIcon}>◈</span>
          <span className={classes.logoText}>SubGen</span>
        </Link>
      </div>
      <nav className={classes.nav}>
        <Link to="/" className={classes.navLink}>Главная</Link>
        <Link to="/dialogs" className={classes.navLink}>Диалоги</Link>
        <Link to="/history" className={classes.navLink}>История</Link>
        <Link to="/about" className={classes.navLink}>О сервисе</Link>
        <Link to="/agreement" className={classes.navLink}>Соглашение</Link>
        {user
          ? <Link to="/profile" className={classes.navLink}>{user.name}</Link>
          : <Link to="/login"   className={classes.navLink}>Войти</Link>
        }
        <Link to="/tasks" className={classes.navLink}>Задачи</Link>
      </nav>
    </header>
  );
}

export default Header;