/* ПР №2: Компонент Header с module.css */
import React from 'react';
import classes from './Header.module.css';

function Header() {
  return (
    <header className={classes.header}>
      <div className={classes.logo}>
        <span className={classes.logoIcon}>◈</span>
        <span className={classes.logoText}>SubGen</span>
      </div>
      <nav className={classes.nav}>
        <a href="#upload" className={classes.navLink}>Загрузить</a>
        <a href="#about" className={classes.navLink}>О сервисе</a>
        <span className={classes.badge}>Beta</span>
      </nav>
    </header>
  );
}

export default Header;
