import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import SubtitleResult from '../components/SubtitleResult';
import Loader from '../components/Loader';
import classes from '../components/SubtitleResult.module.css';
import { t } from '../i18n';

const API = 'http://localhost:8000/api/videos';

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

function Status({ uiLanguage }) {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    let timer;

    const load = async () => {
      try {
        const response = await fetch(`${API}/${id}/status`, { headers: getHeaders() });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || 'Ошибка загрузки статуса');
        if (cancelled) return;
        setJob(data);
        if (data.status === 'pending' || data.status === 'processing') {
          timer = setTimeout(load, 2000);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    };

    load();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [id]);

  const status = job?.status || 'pending';

  return (
    <section className={classes.section}>
      <Link to="/">{t('back', uiLanguage)}</Link>
      <div className={classes.label} style={{ marginTop: 20 }}>
        <span className={classes.labelNum}>02</span>
        <span>{t('statusTitle', uiLanguage)}</span>
      </div>
      {error && <p style={{ color: '#ff4444' }}>{error}</p>}
      {!error && (
        <div className={classes.card}>
          <div className={classes.cardHeader}>
            <span className={classes.cardTitle}>#{id} — {t(status, uiLanguage)}</span>
          </div>
          {(status === 'pending' || status === 'processing') && <Loader />}
          {status === 'failed' && <p style={{ color: '#ff4444' }}>{job?.error_message}</p>}
          {status === 'done' && job && (
            <>
              {job.srt_url && (
                <p>
                  <a href={`http://localhost:8000${job.srt_url}`}>{t('download', uiLanguage)}</a>
                </p>
              )}
              <SubtitleResult result={job} />
            </>
          )}
        </div>
      )}
    </section>
  );
}

export default Status;
