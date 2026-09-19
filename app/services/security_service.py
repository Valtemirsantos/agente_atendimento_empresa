import hashlib
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock


INJECTION_PATTERNS = (
    re.compile(r"\bignore\s+(all\s+)?(previous|prior)\s+instructions?\b", re.IGNORECASE),
    re.compile(r"\bignore\s+(as\s+)?instrucoes\s+anteriores\b", re.IGNORECASE),
    re.compile(r"\b(system prompt|developer message|reveal .*instructions?)\b", re.IGNORECASE),
    re.compile(r"\bexecute\s+(a\s+)?(tool|command|code)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class Principal:
    role: str
    identifier: str


def make_principal(access_key: str, role: str) -> Principal:
    identifier = hashlib.sha256(access_key.encode()).hexdigest()[:16]
    return Principal(role=role, identifier=identifier)


def contains_prompt_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)


class RateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, maximum: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            requests = self._requests[key]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= maximum:
                return False
            requests.append(now)
            return True


rate_limiter = RateLimiter()