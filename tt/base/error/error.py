from __future__ import annotations


class TektonianBaseError(Exception):

    def __init__(self, message: str, context: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        if context:
            self.context = context
