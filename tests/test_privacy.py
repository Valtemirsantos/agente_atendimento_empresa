from app.services.privacy_service import redact_sensitive_data


def test_redige_email_cpf_e_cartao_antes_do_envio():
    message = (
        "Meu e-mail e cliente@example.com, CPF 123.456.789-00 "
        "e cartao 4111 1111 1111 1111."
    )

    redacted = redact_sensitive_data(message)

    assert "cliente@example.com" not in redacted
    assert "123.456.789-00" not in redacted
    assert "4111 1111 1111 1111" not in redacted
    assert "[EMAIL_REDACTED]" in redacted
    assert "[CPF_REDACTED]" in redacted
    assert "[CARD_REDACTED]" in redacted