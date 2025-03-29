from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from models import User, GameSession, Leaderboard
from schemas import SubmitScoreRequest, SubmitScoreResponse, LeaderboardEntry, PlayerRankResponse
from database import SessionLocal
from security import limiter, verify_signature, is_replay, SECRET_KEY
import json
import hmac




# Create an API router with a prefix and tag for grouping endpoints.
router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])

def get_db():
    """
    Dependency to provide a database session.
    It creates a new session for each request and ensures it is closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/submit", response_model=SubmitScoreResponse)
@limiter.limit("10/second")
async def submit_score(
    request: Request,
    payload: SubmitScoreRequest,
    x_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    API endpoint to submit a player's score.

    Validations:
      - HMAC signature verification using SECRET_KEY.
      - Timestamp check to avoid replay attacks.
      - Verifies that the user exists in the 'users' table.
    
    Process:
      1. Reads and decodes the raw request body.
      2. Computes the HMAC signature and compares it with the provided X-Signature header.
      3. Checks if the request is a replay (using timestamp).
      4. Verifies that the user exists.
      5. Inserts a new record in the 'game_sessions' table.
      6. Updates (or creates) the corresponding record in the 'leaderboard' table.
    
    Returns:
      A SubmitScoreResponse indicating that the score was submitted successfully.
    """
    # Read raw request body as bytes and decode to string.
    raw_body = await request.body()
    body_str = raw_body.decode()

    # Debug prints to log request data and signature header.
    print("Received request body:", body_str)
    print("X-Signature header:", x_signature)
    
    # Compute the HMAC signature using the SECRET_KEY.
    computed = hmac.new(SECRET_KEY.encode(), body_str.encode(), digestmod='sha256').hexdigest()
    print("Computed signature:", computed)
    
    # Verify if the provided signature is valid.
    if x_signature is None or not verify_signature(body_str, x_signature):
        raise HTTPException(status_code=400, detail="Invalid or missing HMAC signature")
    
    # Check for replay attack by validating the timestamp.
    if is_replay(payload.timestamp, max_age_seconds=30):
        raise HTTPException(status_code=400, detail="Request timestamp too old (possible replay attack)")
    
    # Verify that the user exists in the 'users' table.
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {payload.user_id} not found.")
    
    # Insert a new game session record for the score submission.
    new_session = GameSession(
        user_id=payload.user_id,
        score=payload.score,
        game_mode=payload.game_mode
    )
    db.add(new_session)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    # Update or create the leaderboard record for the user.
    lb_entry = db.query(Leaderboard).filter(Leaderboard.user_id == payload.user_id).first()
    if lb_entry:
        # If record exists, add the new score to the total score.
        lb_entry.total_score += payload.score
    else:
        # If not, create a new leaderboard record with initial score and rank 0.
        lb_entry = Leaderboard(user_id=payload.user_id, total_score=payload.score, rank=0)
        db.add(lb_entry)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return SubmitScoreResponse(message="Score submitted successfully")

@router.get("/top", response_model=list[LeaderboardEntry])
def get_top_leaderboard(db: Session = Depends(get_db)):
    """
    API endpoint to retrieve the Top 10 leaderboard entries based on the stored rank.

    This endpoint assumes that the 'leaderboard' table has been updated by the POST endpoint.
    It queries the 'leaderboard' table, orders the records by the stored rank (ascending order), and returns the top 10 entries.

    Raises:
      - HTTPException 404 if no leaderboard data is available.

    Returns:
      A list of LeaderboardEntry objects representing the top 10 players.
    """
    # Retrieve leaderboard records ordered by rank and limit to top 10.
    entries = db.query(Leaderboard).order_by(Leaderboard.rank).limit(10).all()
    if not entries:
        raise HTTPException(status_code=404, detail="No leaderboard data available")
    
    result = []
    # For each leaderboard record, fetch the corresponding user's username and create a LeaderboardEntry.
    for entry in entries:
        user = db.query(User).filter(User.id == entry.user_id).first()
        result.append(LeaderboardEntry(
            user_id=entry.user_id,
            username=user.username if user else "Unknown",
            total_score=entry.total_score,
            rank=entry.rank
        ))
    return result

@router.get("/rank/{user_id}", response_model=PlayerRankResponse)
def get_player_rank(user_id: int, db: Session = Depends(get_db)):
    """
    API endpoint to retrieve a specific user's rank from the leaderboard.

    It queries the 'leaderboard' table for the record with the specified user_id.
    
    Raises:
      - HTTPException 404 if the user is not found in the leaderboard.

    Returns:
      A PlayerRankResponse object containing the user's id, username, total score, and rank.
    """
    # Query the leaderboard table for the specified user_id.
    entry = db.query(Leaderboard).filter(Leaderboard.user_id == user_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="User not found in leaderboard")
    
    # Fetch the user's details from the users table.
    user = db.query(User).filter(User.id == user_id).first()
    return PlayerRankResponse(
        user_id=entry.user_id,
        username=user.username if user else "Unknown",
        total_score=entry.total_score,
        rank=entry.rank
    )