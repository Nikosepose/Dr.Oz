"""A single user or bot message."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Message:
    """Carry displayable text and the UTC time when it was created."""

    sender: str
    text: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.sender not in {"user", "bot"}:
            raise ValueError("sender must be 'user' or 'bot'.")
