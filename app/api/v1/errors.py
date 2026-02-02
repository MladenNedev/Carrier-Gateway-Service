from fastapi.responses import JSONResponse

from app.schemas.errors import ErrorDetail, ErrorResponse


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    payload = ErrorResponse(error=ErrorDetail(code=code, message=message)).model_dump()
    return JSONResponse(status_code=status_code, content=payload)
