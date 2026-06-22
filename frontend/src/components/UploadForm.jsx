import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import classes from './UploadForm.module.css';
import { languages, setUiLanguage, t } from '../i18n';
import { VIDEOS_API } from '../config';

const API = VIDEOS_API;

function UploadForm({ uiLanguage, onLanguageChange, onLoading }) {
  const navigate = useNavigate();
  const [mode, setMode] = useState('link');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);
  const [task, setTask] = useState('transcribe');
  const [language, setLanguage] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('ru');
  const [error, setError] = useState('');
  const [availableLanguages, setAvailableLanguages] = useState(languages);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API}/languages`)
      .then((response) => (response.ok ? response.json() : null))
      .then((data) => {
        if (!cancelled && Array.isArray(data?.languages) && data.languages.length > 0) {
          setAvailableLanguages(data.languages);
          if (!data.languages.some((lang) => lang.code === targetLanguage)) {
            setTargetLanguage(data.languages[0].code);
          }
        }
      })
      .catch((err) => {
        console.warn('[Captio API] languages request failed, using local list', err);
      });
    return () => {
      cancelled = true;
    };
  }, [targetLanguage]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const changeUiLanguage = (value) => {
    setUiLanguage(value);
    onLanguageChange(value);
  };

  const changeTask = (value) => {
    setTask(value);
  };

  const isTranslateMode = task === 'translate';

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    onLoading(true);

    const payloadTargetLanguage = targetLanguage || 'en';

    try {
      let response;
      if (mode === 'file') {
        if (!file) throw new Error(t('requiredFile', uiLanguage));
        const form = new FormData();
        form.append('file', file);
        form.append('task', task);
        if (language) form.append('language', language);
        form.append('target_language', payloadTargetLanguage);
        response = await fetch(`${API}/upload`, {
          method: 'POST',
          headers: getAuthHeaders(),
          body: form,
        });
      } else {
        if (!url.trim()) throw new Error(t('requiredUrl', uiLanguage));
        response = await fetch(API, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeaders(),
          },
          body: JSON.stringify({
            video_url: url.trim(),
            task,
            language: language || null,
            target_language: payloadTargetLanguage,
          }),
        });
      }

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data.detail || data.message || `Ошибка сервера: ${response.status}`;
        console.error('[Captio API] video submit failed', {
          status: response.status,
          statusText: response.statusText,
          url: response.url,
          mode,
          task,
          language,
          targetLanguage: payloadTargetLanguage,
          message,
        });
        throw new Error(message);
      }
      navigate(`/status/${data.job_id}`);
    } catch (err) {
      console.error('[Captio UI] video submit error', err);
      setError(err.message);
    } finally {
      onLoading(false);
    }
  }

  return (
    <section className={classes.section} id="upload">
      <div className={classes.label}>
        <span className={classes.labelNum}>01</span>
        <span>{t('source', uiLanguage)}</span>
      </div>
      <form className={classes.form} onSubmit={handleSubmit}>
        <div className={classes.toolbar}>
          <label>
            UI
            <select value={uiLanguage} onChange={(e) => changeUiLanguage(e.target.value)}>
              {languages.slice(0, 2).map((lang) => (
                <option key={lang.code} value={lang.code}>{lang.label}</option>
              ))}
            </select>
          </label>
          <label>
            {t('task', uiLanguage)}
            <select value={task} onChange={(e) => changeTask(e.target.value)}>
              <option value="transcribe">{t('transcribe', uiLanguage)}</option>
              <option value="translate">{t('translate', uiLanguage)}</option>
            </select>
          </label>
          <label>
            {t('language', uiLanguage)}
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="">{t('auto', uiLanguage)}</option>
              {availableLanguages.map((lang) => (
                <option key={lang.code} value={lang.code}>{lang.label}</option>
              ))}
            </select>
          </label>
          <label className={!isTranslateMode ? classes.disabledField : ''}>
            {t('targetLanguage', uiLanguage)}
            <select
              value={isTranslateMode ? targetLanguage : 'disabled'}
              onChange={(e) => setTargetLanguage(e.target.value)}
              disabled={!isTranslateMode}
              aria-disabled={!isTranslateMode}
              title={!isTranslateMode ? 'Недоступно в режиме транскрибации' : undefined}
            >
              {!isTranslateMode && <option value="disabled">Недоступно</option>}
              {availableLanguages.map((lang) => (
                <option key={lang.code} value={lang.code}>{lang.label}</option>
              ))}
            </select>
            {!isTranslateMode && (
              <span className={classes.fieldHint}>Недоступно в режиме транскрибации</span>
            )}
          </label>
        </div>

        <div className={classes.modeTabs}>
          <button type="button" className={mode === 'link' ? classes.activeTab : ''} onClick={() => setMode('link')}>
            {t('link', uiLanguage)}
          </button>
          <button type="button" className={mode === 'file' ? classes.activeTab : ''} onClick={() => setMode('file')}>
            {t('file', uiLanguage)}
          </button>
        </div>

        {mode === 'link' ? (
          <div className={classes.inputWrap}>
            <span className={classes.inputPrefix}>URL →</span>
            <input
              className={classes.input}
              type="text"
              placeholder="https://disk.yandex.ru/d/... или https://youtube.com/..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
        ) : (
          <div className={classes.inputWrap}>
            <span className={classes.inputPrefix}>FILE →</span>
            <input
              className={classes.input}
              type="file"
              accept="video/*,audio/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>
        )}

        {error && <p className={classes.error}>{error}</p>}
        <button className={classes.button} type="submit">
          <span>{t('submit', uiLanguage)}</span>
          <span className={classes.buttonArrow}>→</span>
        </button>
      </form>
    </section>
  );
}

export default UploadForm;
