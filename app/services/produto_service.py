from app.database.connection import get_connection


def consultar_produto(termo: str) -> list[dict[str, object]]:
    """Localiza produtos por nome, sem expor dados sensíveis."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT nome, descricao, preco, estoque
            FROM produtos
            WHERE nome LIKE ? OR descricao LIKE ?
            ORDER BY nome
            """,
            (f"%{termo}%", f"%{termo}%"),
        ).fetchall()
    return [dict(row) for row in rows]