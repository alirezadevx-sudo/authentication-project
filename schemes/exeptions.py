from fastapi import HTTPException, status


class BadRequestErr(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


class ExeptionErr(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)


class NotFoundErr(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=msg)


class UnAuthorizedErr(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

class AccountLockedErr(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=status.HTTP_423_LOCKED, detail=msg)