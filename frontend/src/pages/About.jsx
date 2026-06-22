import React from 'react';
import classes from './About.module.css';

function About() {
  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>03</span>
        <span>О сервисе</span>
      </div>

      <p className={classes.lead}>
        Captio помогает получить субтитры и перевод для видео: пользователь загружает файл
        или отправляет ссылку, а система создает задание, обрабатывает аудиодорожку,
        показывает статус и выдает результат в виде текста и SRT-файла.
      </p>

      <div className={classes.grid}>
        <article className={classes.block}>
          <h3>Что умеет сервис</h3>
          <ul>
            <li>загрузка видео или аудио файла;</li>
            <li>обработка ссылки на видео;</li>
            <li>транскрибация речи через Whisper;</li>
            <li>перевод субтитров на выбранный язык;</li>
            <li>скачивание результата в формате SRT.</li>
          </ul>
        </article>

        <article className={classes.block}>
          <h3>Архитектура</h3>
          <p>
            Frontend реализован на React и Redux Toolkit. Backend построен на FastAPI,
            использует SQLite, JWT-аутентификацию, роли user/admin и фоновые задания
            обработки видео.
          </p>
        </article>

        <article className={classes.block}>
          <h3>Безопасность и эксплуатация</h3>
          <p>
            Пароли хранятся в виде хеша, приватные данные защищены Bearer-токеном,
            права проверяются на сервере. Проект подготовлен к Docker/Render deploy,
            CI/CD и автоматизированному fuzzing-тестированию API.
          </p>
        </article>
      </div>
    </section>
  );
}

export default About;
