from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routers import bot_push, ty_scrap
from utils.logger import setup_logger

logger = setup_logger(__name__)
app = FastAPI()

app.include_router(ty_scrap.router)
app.include_router(bot_push.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"422 Unprocessable Entity: {exc.errors()}", exc_info=True)

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
