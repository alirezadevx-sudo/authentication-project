from fastapi import HTTPException, status

class BasRequestErr(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

class ExeptionErr(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
