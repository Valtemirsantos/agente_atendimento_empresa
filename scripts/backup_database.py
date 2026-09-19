"""Cria um backup SQLite cifrado; nunca deixa uma copia em texto aberto."""

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from app.config.settings import get_settings


def create_encrypted_backup(destination: Path) -> Path:
    settings = get_settings()
    if not settings.backup_encryption_key:
        raise RuntimeError("BACKUP_ENCRYPTION_KEY nao configurada")

    try:
        cipher = Fernet(settings.backup_encryption_key.encode())
    except (TypeError, ValueError) as error:
        raise RuntimeError("BACKUP_ENCRYPTION_KEY invalida") from error

    destination.mkdir(parents=True, exist_ok=True)
    output_path = destination / "empresa.db.fernet"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temporary_file:
        temporary_path = Path(temporary_file.name)
    try:
        source = sqlite3.connect(settings.database_path)
        target = sqlite3.connect(temporary_path)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
        output_path.write_bytes(cipher.encrypt(temporary_path.read_bytes()))
        os.chmod(output_path, 0o600)
    finally:
        temporary_path.unlink(missing_ok=True)
    return output_path


if __name__ == "__main__":
    try:
        create_encrypted_backup(Path("backups"))
    except (RuntimeError, InvalidToken) as error:
        sys.exit(str(error))