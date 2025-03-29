from pydantic import BaseModel, conint, Field
import time

class SubmitScoreRequest(BaseModel):
    user_id: conint(ge=1, le=1000000)  # assuming user IDs between 1 and 1,000,000
    score: conint(ge=0, le=10000)       # score between 0 and 10000
    game_mode: str = "solo"
    timestamp: float = Field(default_factory=lambda: time.time())

class SubmitScoreResponse(BaseModel):
    message: str

class LeaderboardEntry(BaseModel):
    user_id: int
    username: str
    total_score: int
    rank: int

class PlayerRankResponse(BaseModel):
    user_id: int
    username: str
    total_score: int
    rank: int