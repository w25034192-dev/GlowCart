from fastapi import HTTPException, status


class GlowCartError(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str = "error") -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


class NotFoundError(GlowCartError):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, code="not_found")


class ConflictError(GlowCartError):
    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, code="conflict")


class BadRequestError(GlowCartError):
    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, code="bad_request")


class UnauthorizedError(GlowCartError):
    def __init__(self, detail: str = "Authentication required") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, code="unauthorized")


class ForbiddenError(GlowCartError):
    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code="forbidden")

