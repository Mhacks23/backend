from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TranscriptionModel(BaseModel):
    chapter_name: str = Field(...)
    subject_name: str = Field(...)
    user_id: str = Field(...)
    video_url: str = Field(...)


    class Config:
        schema_extra = {
            "example": {
                "chapter_name": "Introduction to Python",
                "subject_name": "Python",
                "user_id": "5f9f5b5b5b5b5b5b5b5b5b5b",
                "video_url": "https://www.youtube.com/watch?v=rfscVS0vtbw",

            }
        }

class OCRToNotesModel(BaseModel):
    chapter_name: str = Field(...)
    subject_name: str = Field(...)
    user_id: str = Field(...)
    text: str = Field(...)

class userDataModel(BaseModel):
    user_id: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "user_id": "sdgsdfsdfsdf1213524"
            }
        }



    class Config:
        schema_extra = {
            "example": {
                "chapter_name": "Introduction to Python",
                "subject_name": "Python",
                "user_id": "5f9f5b5b5b5b5b5b5b5b5b5b",
                "video_url": "https://www.youtube.com/watch?v=rfscVS0vtbw",

            }
        }

def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}