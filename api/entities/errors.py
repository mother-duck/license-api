from fastapi.exceptions import HTTPException

class UnauthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Unauthorized")

class NotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Not Found")

class TooManyRequestsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=429, detail="Too Many Requests")
