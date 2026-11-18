
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load environment variables before importing project modules
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.webhook import router as webhook_router
from src.send_message import router as send_router
from src.config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# Website chat request model
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


# Application startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SAIConnect AI Receptionist is starting...")
    logger.info("Graph API version: %s", settings.GRAPH_API_VERSION)

    logger.info(
        "WhatsApp configured: %s",
        bool(
            settings.WHATSAPP_TOKEN
            and settings.WHATSAPP_PHONE_NUMBER_ID
        ),
    )

    yield

    logger.info("SAIConnect is shutting down...")


# Create FastAPI application
app = FastAPI(
    title="SAIConnect - Sai University AI Receptionist",
    description=(
        "AI-powered multilingual virtual receptionist "
        "for Sai University."
    ),
    version="2.0.0",
    lifespan=lifespan,
)


# Allow local frontend development servers to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only; restrict this in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register existing routers
app.include_router(webhook_router, tags=["WhatsApp Webhook"])

app.include_router(
    send_router,
    prefix="/api",
    tags=["WhatsApp Messaging"],
)


# Home endpoint
@app.get("/", tags=["Health"])
async def home():
    return {
        "status": "running",
        "service": "SAIConnect AI Receptionist",
        "version": "2.0.0",
    }


# Health endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "api_version": settings.GRAPH_API_VERSION,
        "webhook_configured": bool(settings.VERIFY_TOKEN),
        "whatsapp_configured": bool(
            settings.WHATSAPP_TOKEN
            and settings.WHATSAPP_PHONE_NUMBER_ID
        ),
    }


# Website AI chat endpoint
@app.post("/chat", tags=["AI Chat"])
async def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        # Import here so the NLP model loads only when chat is used
        from src.ai.conversation_engine import generate_reply

        reply = generate_reply(request.message)

        return {
            "success": True,
            "reply": reply,
        }

    except Exception:
        logger.exception("SAIConnect website chat failed.")

        raise HTTPException(
            status_code=500,
            detail="SAIConnect AI service is temporarily unavailable.",
        )
