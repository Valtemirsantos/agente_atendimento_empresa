from app.database.connection import get_connection


def consultar_pedido(numero_pedido: str) -> dict[str, object] | None:
    """Retorna somente o estado operacional do pedido solicitado."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT numero, status, previsao_entrega, observacao
            FROM pedidos
            WHERE numero = ?
            """,
            (numero_pedido.strip().upper(),),
        ).fetchone()
    return dict(row) if row else None


def encaminhar_para_atendente(motivo: str) -> str:
    return f"Caso encaminhado para um atendente humano. Motivo registrado: {motivo}"