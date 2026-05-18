import React from "react";
import classes from "./Loader.module.css";

const STAGE_LABELS = {
  queued: "В очереди",
  download_queued: "Ожидает загрузки",
  upload_saved: "Файл принят",
  downloading: "Загрузка",
  preparing: "Подготовка",
  loading_model: "Модель Whisper",
  transcribing: "Распознавание",
  translating: "Перевод",
  writing_srt: "SRT",
  done: "Готово",
  failed: "Ошибка",
};

const ACTIVE_STAGES = [
  "queued",
  "downloading",
  "preparing",
  "loading_model",
  "transcribing",
  "translating",
  "writing_srt",
];

function Loader({ job }) {
  const stage = job?.stage || "queued";
  const progress = Math.max(0, Math.min(100, Number(job?.progress ?? 0)));
  const message = job?.status_message || "Задача поставлена в очередь";

  return (
    <div className={classes.wrap}>
      <div className={classes.visual} aria-hidden="true">
        <div className={classes.videoCard}>
          <div className={classes.playTriangle}>▶</div>
          <div className={classes.waveLine} />
          <div className={classes.subtitleLine} />
        </div>
        <div className={classes.aiOrb}>AI</div>
      </div>

      <div className={classes.progressHeader}>
        <span>{STAGE_LABELS[stage] || stage}</span>
        <span>{progress}%</span>
      </div>
      <div className={classes.progressTrack}>
        <div
          className={classes.progressFill}
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className={classes.stepText}>{message}</p>
      <div className={classes.timeline}>
        {ACTIVE_STAGES.map((item) => (
          <span
            key={item}
            className={`${classes.dot} ${item === stage ? classes.activeDot : ""} ${ACTIVE_STAGES.indexOf(item) < ACTIVE_STAGES.indexOf(stage) ? classes.doneDot : ""}`}
            title={STAGE_LABELS[item] || item}
          />
        ))}
      </div>
    </div>
  );
}

export default Loader;
