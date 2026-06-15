import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.services.queue_worker import start_background_workers
from app.services.database import connect_to_mongo, close_mongo_connection
from app.config import settings

# Configure basic logging for the entry point
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Initializing system dependencies...")
    await connect_to_mongo()

    await start_background_workers(num_workers=3) 
    
    yield
    
    logger.info("Tearing down system dependencies...")
    await close_mongo_connection()

app = FastAPI(
    title="AI Coding Interview Assistant",
    version="1.0.0",
    lifespan=lifespan
)

ALLOWED_ORIGINS = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)