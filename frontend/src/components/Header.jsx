import React from 'react';
import { Link } from 'react-router-dom';
import classes from './Header.module.css';

function Header() {
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
      </nav>
    </header>
  );
}

export default Header;