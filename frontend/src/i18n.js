export const languages = [
  { code: 'ru', label: 'Русский' },
  { code: 'en', label: 'English' },
  { code: 'es', label: 'Español' },
  { code: 'de', label: 'Deutsch' },
  { code: 'fr', label: 'Français' },
  { code: 'it', label: 'Italiano' },
  { code: 'pt', label: 'Português' },
  { code: 'pl', label: 'Polski' },
  { code: 'tr', label: 'Türkçe' },
  { code: 'uk', label: 'Українська' },
  { code: 'kk', label: 'Қазақша' },
  { code: 'zh-CN', label: '中文' },
  { code: 'ja', label: '日本語' },
  { code: 'ko', label: '한국어' },
  { code: 'ar', label: 'العربية' },
];

const dictionary = {
  ru: {
    heroTag: 'AI Subtitle Generator',
    titlePrefix: 'Субтитры за',
    titleAccent: 'минуты',
    heroSub: 'Загрузите видео с компьютера или по ссылке — Whisper распознает речь и сформирует субтитры с таймкодами.',
    source: 'Источник видео',
    link: 'Ссылка',
    file: 'Файл',
    videoLink: 'Ссылка на видео',
    uploadFile: 'Файл с компьютера',
    chooseFile: 'Выберите видеофайл',
    task: 'Режим',
    transcribe: 'Транскрибация',
    translate: 'Перевод',
    language: 'Исходный язык',
    targetLanguage: 'Целевой язык',
    auto: 'Авто',
    submit: 'Запустить обработку',
    requiredUrl: 'Введите ссылку на видео',
    requiredFile: 'Выберите видеофайл',
    statusTitle: 'Статус обработки',
    pending: 'Задача поставлена в очередь',
    processing: 'Видео обрабатывается',
    done: 'Готово',
    failed: 'Ошибка обработки',
    back: '← На главную',
    download: 'Скачать .srt',
  },
  en: {
    heroTag: 'AI Subtitle Generator',
    titlePrefix: 'Subtitles in',
    titleAccent: 'minutes',
    heroSub: 'Upload a video from your computer or via link. Whisper will recognize speech and create timestamped subtitles.',
    source: 'Video source',
    link: 'Link',
    file: 'File',
    videoLink: 'Video link',
    uploadFile: 'File from computer',
    chooseFile: 'Choose a video file',
    task: 'Mode',
    transcribe: 'Transcribe',
    translate: 'Translate',
    language: 'Source language',
    targetLanguage: 'Target language',
    auto: 'Auto',
    submit: 'Start processing',
    requiredUrl: 'Enter a video link',
    requiredFile: 'Choose a video file',
    statusTitle: 'Processing status',
    pending: 'Queued',
    processing: 'Processing video',
    done: 'Done',
    failed: 'Processing failed',
    back: '← Home',
    download: 'Download .srt',
  },
};

export function getUiLanguage() {
  return localStorage.getItem('uiLanguage') || 'ru';
}

export function setUiLanguage(lang) {
  localStorage.setItem('uiLanguage', lang);
}

export function t(key, lang = getUiLanguage()) {
  return dictionary[lang]?.[key] || dictionary.ru[key] || key;
}

export function getStatusText(job, lang = getUiLanguage()) {
  if (job?.status_message) return job.status_message;
  return t(job?.status || 'pending', lang);
}
