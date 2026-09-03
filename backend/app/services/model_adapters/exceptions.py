"""Errors raised by ML adapters when teammate models are not connected."""


class ModelNotIntegratedError(Exception):
    """Raised when a teammate ML model has not been connected yet."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)
