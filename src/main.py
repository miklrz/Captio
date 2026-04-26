from fastapi import FastAPI, HTTPException
from src.pydantic_models import VideoRequest, VideoResponse
from src.helpers import load_video_from_youtube, get_new_video_path, load_video_from_yd
from src.model import load_whisper_model, transcribe_audio
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()


@app.post("/upload-video")
def upload_video(request: VideoRequest):
    url = request.video_url
    logger.info(f"Получен запрос с url: {url}")
    path_to_load_video = get_new_video_path(url=url, type="yandex")

    success = load_video_from_yd(url=url, path=path_to_load_video)
    if not success:
        logger.error(f"Ошибка обработки видео")
        raise HTTPException(status_code=500)
    model = load_whisper_model(model_name="large-v3", device="auto")
    result = transcribe_audio(model, audio_path=path_to_load_video)
    return VideoResponse(text=result["text"])


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)
