import React from 'react';
import UploadForm from '../components/UploadForm';
import SubtitleResult from '../components/SubtitleResult';
import Loader from '../components/Loader';
import { t } from '../i18n';

function Home({ result, setResult, loading, setLoading, uiLanguage, setUiLanguage }) {
  return (
    <>
      <section className="hero">
        <span className="heroTag">{t('heroTag', uiLanguage)}</span>
        <h1 className="heroTitle">
          {t('titlePrefix', uiLanguage)}&nbsp;
          <span className="heroAccent">{t('titleAccent', uiLanguage)}</span>
        </h1>
        <p className="heroSub">{t('heroSub', uiLanguage)}</p>
      </section>

      <UploadForm
        onResult={setResult}
        onLoading={setLoading}
        uiLanguage={uiLanguage}
        onLanguageChange={setUiLanguage}
      />

      {loading && <Loader />}
      {result && !loading && <SubtitleResult result={result} />}
    </>
  );
}

export default Home;
