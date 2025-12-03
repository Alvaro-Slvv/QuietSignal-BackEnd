from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import Base, engine

from .common.apiResponse import APIResponse
from fastapi.responses import JSONResponse

from .api.routers.authRoutes import router as authRouter
from .api.routers.analyzeRoutes import router as analyzrouter
from .api.routers.userRoutes import router as userRouter
from .database.dbInitializer import initialize_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield 
app = FastAPI(title="QuietSignal - Mood Diary (Modular DAO MVP)")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            message=exc.detail,
            code=exc.status_code
        ).model_dump()
    )

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
