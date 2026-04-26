from fastapi import FastAPI
from src.pydantic_models import VideoRequest
from src.helpers import load_video_from_youtube, get_new_video_path
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/upload-video")
def upload_video(request: VideoRequest):
    url = request.video_url
    logger.info(f"Получен запрос с url: {url}")
    path_to_load_video = get_new_video_path(url=url)
    load_video_from_youtube(url=url, path=path_to_load_video)
