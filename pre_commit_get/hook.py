from __future__ import annotations

from typing import Any
from typing import NamedTuple


class Hook(NamedTuple):
    src: str
    id: str
    name: str | None
    description: str | None
    args: list[str] | None

    @classmethod
    def create(cls, d: dict[str, Any], *, src: str) -> Hook:
        return cls(
            src,
            d['id'],
            d.get('name'),
            d.get('description'),
            d.get('args'),
        )
