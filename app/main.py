
# ==========================================
# 1. IMPORT STANDARD LIBRARIES
# ==========================================

from contextlib import asynccontextmanager
from pathlib import Path
import os
import logging


# ==========================================
# 2. LOAD ENVIRONMENT
# ==========================================

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


# ==========================================
# 3. IMPORT EXTERNAL LIBRARIES
# ==========================================

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from openai import OpenAIError

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from langgraph.checkpoint.postgres import PostgresSaver


# ==========================================
# 4. IMPORT PROJECT MODULES
# ==========================================

from app.core.logging_config import setup_logging

from app.core.database import (
    Base,
    engine,
    get_db
)

from app.core.dependencies import get_current_user


# Database Models
from app.models.user import User
from app.models.ticket import Ticket
from app.models.order import Order
from app.models.conversation import Conversation
from app.models.product import Product


# API Routers
from app.api.ticket import router as ticket_router
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.conversation import router as conversation_router


# Schemas
from app.schemas.chat import ChatRequest, ChatResponse


# Services
from app.services.llm_service import LLMConfigurationError


# LangGraph
from app.agents.tool_call_demo import build_tool_call_graph


# ==========================================
# 5. LOGGING
# ==========================================

setup_logging()

logger = logging.getLogger(__name__)


# ==========================================
# 6. APPLICATION LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # 1. Tạo các bảng nghiệp vụ
    Base.metadata.create_all(bind=engine)

    # 2. Lấy PostgreSQL URL cho LangGraph
    database_url = os.getenv("LANGGRAPH_DATABASE_URL")

    if not database_url:

        raise RuntimeError(
            "LANGGRAPH_DATABASE_URL is missing"
        )

    # 3. Tạo Connection Pool
    pool = ConnectionPool(
        conninfo=database_url,
        min_size=1,
        max_size=10,
        kwargs={
            "autocommit": True,
            "row_factory": dict_row
        },
        open=False
    )

    try:

        # 4. Mở Connection Pool
        pool.open()

        # 5. Khởi tạo PostgreSQL Checkpointer
        checkpointer = PostgresSaver(pool)

        # 6. Tạo bảng checkpoint nếu chưa có
        checkpointer.setup()

        # 7. Khởi tạo Multi-Tool Agent Graph
        app.state.tool_agent_graph = build_tool_call_graph(
            checkpointer
        )

        logger.info(
            "PostgreSQL Checkpointer initialized successfully"
        )

        logger.info(
            "Multi-Tool Agent Graph initialized successfully"
        )

        yield

    finally:

        # 8. Đóng Connection Pool khi ứng dụng dừng
        pool.close()

        logger.info(
            "PostgreSQL Connection Pool closed"
        )


# ==========================================
# 7. CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Enterprise Customer Support AI Agent",
    description="AI-powered customer support backend",
    version="0.1.0",
    lifespan=lifespan
)


# ==========================================
# 8. BASIC ENDPOINTS
# ==========================================

@app.get("/")
def root():

    return {
        "message": "Enterprise Customer Support AI Agent",
        "status": "running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "ok"
    }


@app.get("/about")
def about():

    return {
        "project": "Enterprise Customer Support AI Agent",
        "version": "1.0",
        "developer": "Phat"
    }


# ==========================================
# 9. CHAT ENDPOINT
# ==========================================

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:

        # 1. Kiểm tra Conversation thuộc người dùng
        statement = select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        )

        conversation = db.scalar(statement)

        if conversation is None:

            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        # 2. Lấy Multi-Tool Agent Graph
        agent_graph = http_request.app.state.tool_agent_graph

        # 3. Gọi LangGraph
        result = agent_graph.invoke(
            {
                "user_message": request.message,

                "input_mode": "user",

                "tool_calls": [],

                "tool_outputs": [],

                "tool_rounds": 0
            },

            config={
                "configurable": {

                    # Mỗi Conversation có một Thread riêng
                    "thread_id": f"tool-agent-{conversation.id}",

                    # Database Session nghiệp vụ
                    "db": db,

                    # User ID lấy từ JWT
                    "user_id": current_user.id
                }
            }
        )

        # 4. Trả câu trả lời
        return ChatResponse(
            reply=result["reply"]
        )

    except HTTPException:

        raise

    except LLMConfigurationError:

        logger.exception("LLM configuration error")

        raise HTTPException(
            status_code=503,
            detail="LLM API is not configured"
        )

    except OpenAIError:

        logger.exception("OpenAI API error")

        raise HTTPException(
            status_code=502,
            detail="AI service is unavailable"
        )

    except Exception:

        logger.exception("Unexpected chat endpoint error")

        raise HTTPException(
            status_code=500,
            detail="Internal AI Agent error"
        )


# ==========================================
# 10. REGISTER ROUTERS
# ==========================================

app.include_router(ticket_router)

app.include_router(auth_router)

app.include_router(user_router)

app.include_router(conversation_router)
