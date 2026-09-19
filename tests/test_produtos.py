from app.database.connection import initialize_database
from app.services.produto_service import consultar_produto


def test_consulta_produto_por_nome(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'empresa.db'}")
    from app.config.settings import get_settings

    get_settings.cache_clear()
    initialize_database()

    produtos = consultar_produto("Profissional")

    assert len(produtos) == 1
    assert produtos[0]["nome"] == "Plano Profissional"
    get_settings.cache_clear()