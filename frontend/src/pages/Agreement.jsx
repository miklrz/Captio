import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { toggleCheckbox, acceptAgreement, resetAgreement } from '../redux/agreementSlice';
import classes from './Agreement.module.css';

function Agreement() {
  const dispatch = useDispatch();

  // Читаем состояние из Redux store
  const isChecked  = useSelector(state => state.agreement.isChecked);
  const isAccepted = useSelector(state => state.agreement.isAccepted);

  // Если соглашение уже принято — показываем экран успеха
  if (isAccepted) {
    return (
      <div className={classes.success}>
        <span className={classes.successIcon}>✓</span>
        <h2 className={classes.successTitle}>Соглашение принято</h2>
        <p className={classes.successText}>
          Спасибо! Вы успешно приняли пользовательское соглашение.
        </p>
        <button
          className={classes.resetBtn}
          onClick={() => dispatch(resetAgreement())}
        >
          Сбросить
        </button>
      </div>
    );
  }

  return (
    <section className={classes.section}>
      <div className={classes.header}>
        <span className={classes.labelNum}>05</span>
        <span>Пользовательское соглашение</span>
      </div>

      <div className={classes.card}>
        <h2 className={classes.title}>Условия использования SubGen</h2>

        {/* Текст соглашения */}
        <div className={classes.text}>
          <p>
            Настоящее Пользовательское соглашение регулирует условия использования
            сервиса SubGen для автоматической генерации субтитров.
          </p>
          <p>
            Используя сервис, вы соглашаетесь с тем, что загружаемые материалы
            не нарушают авторских прав третьих лиц, а также не содержат
            запрещённого законодательством контента.
          </p>
          <p>
            Сервис предоставляется «как есть». Мы не несём ответственности за
            точность распознавания речи и качество генерируемых субтитров.
            Все данные обрабатываются на серверах с соблюдением политики
            конфиденциальности.
          </p>
          <p>
            Продолжая использование сервиса, вы подтверждаете, что ознакомились
            с данным соглашением и принимаете его условия в полном объёме.
          </p>
        </div>

        {/* Чекбокс — dispatch action при клике */}
        <label className={classes.checkLabel}>
          <input
            type="checkbox"
            className={classes.checkbox}
            checked={isChecked}
            onChange={() => dispatch(toggleCheckbox())}
          />
          <span>Я ознакомился с соглашением и принимаю его условия</span>
        </label>

        {/* Кнопка активна только если чекбокс отмечен */}
        <button
          className={classes.btn}
          disabled={!isChecked}
          onClick={() => dispatch(acceptAgreement())}
        >
          Подтвердить соглашение
        </button>
      </div>
    </section>
  );
}

export default Agreement;