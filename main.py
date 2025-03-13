from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from routers import bot_push, ty_scrap
from utils.logger import setup_logger

logger = setup_logger(__name__, "app")
app = FastAPI()

app.include_router(ty_scrap.router)
app.include_router(bot_push.router)


# 422 Request Validation Error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"422 Unprocessable Entity: {exc.errors()}", exc_info=False)

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# 429 Too Many Requests
@app.exception_handler(RateLimitExceeded)
async def ratelimit_exception_handler(request: Request, exc: RateLimitExceeded):
    logger.error(f"429 Too Many Requests from {request.client.host}", exc_info=False)
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )
