import sqlite3
from pathlib import Path

from app.config.settings import get_settings


def get_connection() -> sqlite3.Connection:
    database_path = Path(get_settings().database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT NOT NULL,
                preco REAL NOT NULL,
                estoque INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pedidos (
                numero TEXT PRIMARY KEY,
                cliente_nome TEXT NOT NULL,
                status TEXT NOT NULL,
                previsao_entrega TEXT,
                observacao TEXT
            );

            CREATE TABLE IF NOT EXISTS conversas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sessao_id TEXT NOT NULL,
                mensagem_cliente TEXT NOT NULL,
                resposta_assistente TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO produtos (id, nome, descricao, preco, estoque)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (1, "Plano Essencial", "Suporte em horario comercial.", 99.90, 50),
                (2, "Plano Profissional", "Suporte prioritario e relatorios.", 199.90, 25),
            ],
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO pedidos (numero, cliente_nome, status, previsao_entrega, observacao)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("PED-1001", "Cliente Exemplo", "em separacao", "2026-09-25", None),
        )


def delete_expired_conversations(retention_days: int) -> None:
    """Exclui automaticamente registros de conversa fora do prazo de retenção."""
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM conversas WHERE criado_em < datetime('now', ?)",
            (f"-{retention_days} days",),
        )