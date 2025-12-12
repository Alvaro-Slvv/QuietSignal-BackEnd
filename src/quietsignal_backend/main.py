from fastapi import FastAPI
from contextlib import asynccontextmanager

from quietsignal_backend.database import Base, engine
from quietsignal_backend.database.dbInitializer import initialize_database

# Routers
from quietsignal_backend.api.routers.authRoutes import router as authRouter
from quietsignal_backend.api.routers.userRoutes import router as userRouter
from quietsignal_backend.api.routers.journalRoutes import router as journalRouter
from quietsignal_backend.api.routers.analyzeRoutes import router as analyzeRouter
from quietsignal_backend.api.routers.adminRoutes import router as adminRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">>> FastAPI lifespan starting...")
    initialize_database()
    print(">>> Startup complete.")
    yield
    print(">>> FastAPI lifespan shutting down...")


app = FastAPI(
    title="QuietSignal Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Register routers
app.include_router(authRouter)
app.include_router(userRouter)
app.include_router(journalRouter)
app.include_router(analyzeRouter)
app.include_router(adminRouter)



@app.get("/")
def root():
    return {"message": "QuietSignal backend running"}
