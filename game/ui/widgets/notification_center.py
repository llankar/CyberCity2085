"""Centralized lightweight notifications for UI feedback consistency."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Notification:
    level: str
    text: str


@dataclass
class NotificationCenter:
    """Small in-memory notification stream for UI actions."""

    max_items: int = 12
    _items: list[Notification] = field(default_factory=list)

    def push(self, level: str, text: str) -> Notification:
        note = Notification(level=level, text=text)
        self._items.append(note)
        if len(self._items) > self.max_items:
            self._items = self._items[-self.max_items :]
        return note

    def success(self, text: str) -> Notification:
        return self.push("success", text)

    def warning(self, text: str) -> Notification:
        return self.push("warning", text)

    def failure(self, text: str) -> Notification:
        return self.push("failure", text)

    def latest_text_lines(self, limit: int = 5) -> list[str]:
        return [f"[{n.level.upper()}] {n.text}" for n in self._items[-limit:]][::-1]
