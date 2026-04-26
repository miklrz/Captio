from pydantic import BaseModel, Field


class VideoRequest(BaseModel):
    """
    Запрос с видео
    """

    video_url: str = Field(..., description="Ссылка на видео")
