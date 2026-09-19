from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    mensagem: str = Field(min_length=1, max_length=2_000)
    sessao_id: str = Field(min_length=1, max_length=100)


class ChatResponse(BaseModel):
    resposta: str
    encaminhado: bool = False