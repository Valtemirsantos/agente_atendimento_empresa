import hashlib
import hmac
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.agents.atendimento_agent import create_agent
from app.config.settings import get_settings
from app.database.connection import delete_expired_conversations, get_connection
from app.database.models import ChatRequest, ChatResponse
from app.services.pedido_service import encaminhar_para_atendente
from app.services.privacy_service import redact_sensitive_data
from app.services.security_service import (
    Principal,
    contains_prompt_injection,
    make_principal,
    rate_limiter,
)

router = APIRouter(prefix="/api/atendimento", tags=["atendimento"])


def verify_internal_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
) -> Principal:
    access_keys = get_settings().configured_access_keys
    if not access_keys:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Autenticacao do servico nao configurada.",
        )
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de acesso invalida.",
        )
    for access_key, role in access_keys.items():
        if secrets.compare_digest(x_api_key, access_key):
            if role not in {"support", "admin"}:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permissao insuficiente para atendimento.",
                )
            return make_principal(access_key, role)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Chave de acesso invalida.",
    )


def enforce_rate_limit(request: Request, principal: Principal) -> None:
    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    client_key = f"{principal.identifier}:{client_host}"
    if not rate_limiter.allow(
        client_key,
        settings.rate_limit_requests,
        settings.rate_limit_window_seconds,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Limite de requisicoes excedido. Tente novamente mais tarde.",
        )


def save_conversation(request: ChatRequest) -> None:
    settings = get_settings()
    hash_key = settings.conversation_hash_key or settings.internal_api_key
    if not hash_key:
        raise RuntimeError("CONVERSATION_HASH_KEY nao configurada")

    session_hash = hmac.new(
        hash_key.encode(),
        request.sessao_id.encode(),
        hashlib.sha256,
    ).hexdigest()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO conversas (sessao_id, mensagem_cliente, resposta_assistente)
            VALUES (?, ?, ?)
            """,
            (session_hash, "[CONTEUDO_NAO_ARMAZENADO]", "[CONTEUDO_NAO_ARMAZENADO]"),
        )
    delete_expired_conversations(settings.conversation_retention_days)


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    http_request: Request,
    principal: Annotated[Principal, Depends(verify_internal_api_key)],
) -> ChatResponse:
    enforce_rate_limit(http_request, principal)
    sanitized_message = redact_sensitive_data(payload.mensagem)
    if contains_prompt_injection(sanitized_message):
        response = encaminhar_para_atendente(
            "Solicitacao com instrucoes nao permitidas para o atendimento automatizado."
        )
        save_conversation(payload)
        return ChatResponse(resposta=response, encaminhado=True)

    try:
        result = create_agent().run(sanitized_message, session_id=payload.sessao_id)
        response = result.content if isinstance(result.content, str) else str(result.content)
        forwarded = False
    except RuntimeError:
        response = encaminhar_para_atendente(
            "O atendimento por IA ainda nao foi configurado pela empresa."
        )
        forwarded = True

    save_conversation(payload)
    return ChatResponse(resposta=response, encaminhado=forwarded)