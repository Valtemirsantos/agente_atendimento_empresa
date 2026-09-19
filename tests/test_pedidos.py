from app.database.connection import initialize_database
from app.services.pedido_service import consultar_pedido


def test_consulta_pedido_existente(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'empresa.db'}")
    from app.config.settings import get_settings

    get_settings.cache_clear()
    initialize_database()

    pedido = consultar_pedido("ped-1001")

    assert pedido is not None
    assert pedido["status"] == "em separacao"
    get_settings.cache_clear()