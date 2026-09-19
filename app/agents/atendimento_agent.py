from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.config.settings import get_settings
from app.services.pedido_service import consultar_pedido, encaminhar_para_atendente
from app.services.produto_service import consultar_produto


INSTRUCTIONS = """
Voce e o assistente de atendimento da empresa. Responda em portugues brasileiro.
Use consultar_produto para duvidas sobre produtos e consultar_pedido quando receber
o numero do pedido. Nunca invente status, preco, prazo ou politicas. Solicite o
numero do pedido quando ele for necessario. Encaminhe para um atendente humano em
casos de reclamacao, cancelamento, reembolso, dados pessoais ou quando nao puder
resolver com as ferramentas. Nao solicite senhas, cartoes ou documentos completos.
""".strip()


def create_agent() -> Agent:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY nao configurada")

    return Agent(
        model=OpenAIChat(id=settings.openai_model, api_key=settings.openai_api_key),
        tools=[consultar_produto, consultar_pedido, encaminhar_para_atendente],
        instructions=INSTRUCTIONS,
        markdown=False,
    )