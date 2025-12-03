from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import Base, engine

from .api.routers.authRoutes import router as authRouter
from .api.routers.analyzeRoutes import router as analyzrouter
from .api.routers.userRoutes import router as userRouter
from .database.dbInitializer import initialize_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield 
app = FastAPI(title="QuietSignal - Mood Diary (Modular DAO MVP)")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(authRouter)
app.include_router(analyzrouter)
app.include_router(userRouter)

# create tables for dev
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"status": "ok", "app": "QuietSignal Mood Diary API (modular)"}
