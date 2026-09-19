import re

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
CPF_PATTERN = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
CARD_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


def _is_luhn_valid(value: str) -> bool:
    digits = [int(digit) for digit in value if digit.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False

    checksum = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def redact_sensitive_data(text: str) -> str:
    """Remove identificadores pessoais antes de o texto sair do servidor."""
    redacted = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)
    redacted = CPF_PATTERN.sub("[CPF_REDACTED]", redacted)
    return CARD_PATTERN.sub(
        lambda match: "[CARD_REDACTED]" if _is_luhn_valid(match.group()) else match.group(),
        redacted,
    )