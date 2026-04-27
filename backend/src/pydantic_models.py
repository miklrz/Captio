from pydantic import BaseModel, Field


class VideoRequest(BaseModel):
    """
    Запрос с видео
    """

    video_url: str = Field(..., description="Ссылка на видео")


class VideoResponse(BaseModel):
    """
    Ответ сервиса - субтитры
    """

    text: str = Field(..., description="Текст субтитров")
