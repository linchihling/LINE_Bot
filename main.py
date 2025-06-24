from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from routers import ths_bot, ty_scrap
from utils.factory import setup_logger

logger = setup_logger(__name__)
app = FastAPI()

app.include_router(ty_scrap.router)
app.include_router(ths_bot.router)


# 422 Request Validation Error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        "422 Request Validation Error",
        exc_info=False,
        extra={"project": request.client.host},
    )
    print(exc.errors())

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# 429 Too Many Requests
@app.exception_handler(RateLimitExceeded)
async def ratelimit_exception_handler(request: Request, exc: RateLimitExceeded):
    logger.error(
        "429 Too Many Requests", exc_info=False, extra={"project": request.client.host}
    )
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )
