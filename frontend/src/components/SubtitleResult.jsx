/* ПР №2: Компонент отображения результата */
import React, { useState } from 'react';
import classes from './SubtitleResult.module.css';

function SubtitleResult({ result }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(result.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleDownload() {
    const srt = result.segments
      ? result.segments
          .map((seg, i) =>
            `${i + 1}\n${formatTime(seg.start)} --> ${formatTime(seg.end)}\n${seg.text.trim()}\n`
          )
          .join('\n')
      : result.text;

    const blob = new Blob([srt], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'subtitles.srt';
    a.click();
  }

  function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.round((seconds % 1) * 1000);
    return `${pad(h)}:${pad(m)}:${pad(s)},${padMs(ms)}`;
  }

  function pad(n) { return String(n).padStart(2, '0'); }
  function padMs(n) { return String(n).padStart(3, '0'); }

  return (
    <section className={classes.section} id="result">
      <div className={classes.label}>
        <span className={classes.labelNum}>02</span>
        <span>Результат</span>
        <span className={classes.successDot} />
      </div>

      <div className={classes.card}>
        <div className={classes.cardHeader}>
          <span className={classes.cardTitle}>Транскрипция</span>
          <div className={classes.actions}>
            <button className={classes.actionBtn} onClick={handleCopy}>
              {copied ? '✓ Скопировано' : 'Копировать'}
            </button>
            <button
              className={`${classes.actionBtn} ${classes.actionBtnPrimary}`}
              onClick={handleDownload}
            >
              ↓ .srt
            </button>
          </div>
        </div>
        <div className={classes.textBody}>
          {result.segments ? (
            result.segments.map((seg, i) => (
              <div key={i} className={classes.segment}>
                <span className={classes.timestamp}>
                  {formatTime(seg.start)}
                </span>
                <p className={classes.segText}>{seg.text}</p>
              </div>
            ))
          ) : (
            <p className={classes.fullText}>{result.text}</p>
          )}
        </div>
      </div>
    </section>
  );
}

export default SubtitleResult;
