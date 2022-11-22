"""Exceptions used for parse errors."""

class QueryParseError(Exception):
    """Exception for parsing errors."""

    def __init__(self, query: str) -> None:
        super().__init__()
        self.query = query

    def __str__(self) -> str:
        return f"Unable to parse: {self.query}"
