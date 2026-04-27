/* ПР №2: Компонент индикатора загрузки */
import React from 'react';
import classes from './Loader.module.css';

const STEPS = [
  'Скачиваем видео с Яндекс Диска...',
  'Извлекаем аудиодорожку (FFmpeg)...',
  'Whisper анализирует речь...',
  'Формируем субтитры...',
];

function Loader() {
  const [step, setStep] = React.useState(0);

  React.useEffect(() => {
    const id = setInterval(() => {
      setStep((s) => (s + 1) % STEPS.length);
    }, 3000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className={classes.wrap}>
      <div className={classes.ring}>
        <div className={classes.ringInner} />
      </div>
      <p className={classes.stepText}>{STEPS[step]}</p>
      <p className={classes.hint}>Обработка занимает 1–5 минут</p>
    </div>
  );
}

export default Loader;
