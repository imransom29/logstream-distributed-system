import newrelic.agent
newrelic.agent.initialize('newrelic.ini')  # Ensure newrelic.ini exists and is configured properly

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from api import leaderboard
from database import engine, Base
from security import limiter
import uvicorn

app = FastAPI(title="Gaming Leaderboard - Secure Edition")

# Create all tables (if they do not exist)
Base.metadata.create_all(bind=engine)

# Attach the limiter to the app state so SlowAPI can access it.
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Setup templates directory.
templates = Jinja2Templates(directory="templates")

# Middleware: Add Content Security Policy header (for XSS mitigation)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' https://cdn.jsdelivr.net"
    return response

# Serve the index.html UI
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(leaderboard.router)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return Response(content="Too many requests, please slow down.", status_code=429)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)