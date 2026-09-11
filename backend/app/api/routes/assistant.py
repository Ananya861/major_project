"""API routes for Multilingual AI Assistant."""

from typing import Any
from fastapi import APIRouter, Query
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.services.assistant_service import (
    SUPPORTED_LANGUAGES,
    process_assistant_chat,
)

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_assistant(
    request: AssistantChatRequest,
) -> AssistantChatResponse:
    """Process a message and return intelligent, context-aware agricultural advice."""
    response_text, lang, suggestions, context_used = process_assistant_chat(
        message=request.message,
        language=request.language,
        context=request.context,
    )

    return AssistantChatResponse(
        response=response_text,
        language=lang,
        suggestions=suggestions,
        context_used=context_used,
    )


@router.get("/languages")
async def get_supported_languages() -> dict[str, str]:
    """Return list of supported languages."""
    return SUPPORTED_LANGUAGES


@router.get("/suggestions")
async def get_suggestions(
    language: str = Query(default="en", max_length=10),
) -> dict[str, Any]:
    """Return default quick-start suggestions in the requested language."""
    _, lang, suggestions, _ = process_assistant_chat(
        message="help",
        language=language,
        context=None,
    )
    return {"language": lang, "suggestions": suggestions}
