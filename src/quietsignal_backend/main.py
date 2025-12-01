from fastapi import FastAPI

from .routes import auth_routes, analyze_routes
from .database import Base, engine

# Create tables at startup (MVP)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QuietSignal Mood Diary API",
    version="0.1.0",
    description="MVP backend with auth + sentiment analysis",
)

app.include_router(auth_routes.router)
app.include_router(analyze_routes.router)


@app.get("/")
def read_root():
    return {"message": "QuietSignal API is running"}
