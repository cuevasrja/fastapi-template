class ResourceNotFoundException(Exception):
    def __init__(self, resource: str = "Resource", id: str | None = None):
        detail = f"{resource} not found"
        if id:
            detail = f"{resource} with id '{id}' not found"
        super().__init__(detail)
        self.detail = detail


class ForbiddenException(Exception):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail)
        self.detail = detail


class ConflictException(Exception):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(detail)
        self.detail = detail


class UnauthorizedException(Exception):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(detail)
        self.detail = detail
