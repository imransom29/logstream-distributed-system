from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    join_date = Column(DateTime, server_default=func.current_timestamp())

class GameSession(Base):
    __tablename__ = 'game_sessions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False)
    game_mode = Column(String(50), nullable=False)
    timestamp = Column(DateTime, server_default=func.current_timestamp())

class Leaderboard(Base):
    __tablename__ = 'leaderboard'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    total_score = Column(Integer, nullable=False)
    # We'll compute rank on the fly so the stored rank is not used.
    rank = Column(Integer)