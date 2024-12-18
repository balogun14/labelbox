from pydantic import BaseModel
from datetime import datetime


class ChallengeBase(BaseModel):
    title: str
    description: str


class ChallengeCreate(ChallengeBase):
    file_url: str


class Challenge(ChallengeBase):
    id: int
    file_url: str
    created_at: datetime

    class Config:
        orm_mode = True
