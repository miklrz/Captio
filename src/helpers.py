from pytube import YouTube
import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_video_from_youtube(url: str, path: str) -> bool:
    try:
        # yt = YouTube(url)
        # stream = yt.streams.get_highest_resolution()
        # stream = yt.streams.filter(res="1080p").first()
        # stream.download(output_path=path)
        import yt_dlp

        ydl_opts = {
            "format": "bestaudio/best",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "external_downloader": "aria2c",  # Используем aria2 для ускорения
            "external_downloader_args": [
                "-x",
                "16",
                "-s",
                "16",
                "-k",
                "1M",
            ],  # 16 потоков
            "outtmpl": path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        import time

        start_time = time.time()

        with yt_dlp.YoutubeDL({"format": "bestaudio/best"}) as ydl:
            print("Начинаю извлечение инфо...")
            info = ydl.extract_info(url, download=False)
            print(f"Инфо получено за {time.time() - start_time:.2f} секунд")

        # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        #     ydl.download([url])

        logger.info(f"Видео загружено: {path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при загрузке видео: {e}")
        return False


def get_new_video_path(url: str) -> Path:
    now = datetime.datetime.now().replace(microsecond=0)
    url_id = url.lstrip("https://www.youtube.com/watch?v=")
    filename = url_id + "_" + str(now).replace(" ", "_")
    full_path = Path("data/uploads/") / filename
    logger.info(f"Полный путь, по которому будет загружено видео: {full_path}")
    return full_path
