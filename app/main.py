from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.services.queue_worker import start_background_workers
from app.services.database import connect_to_mongo, close_mongo_connection

app = FastAPI(
    title="AI Coding Interview Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    await start_background_workers(num_workers=3)

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()