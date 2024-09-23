from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
# from fastapi_profiler import PyInstrumentProfilerMiddleware
from starlette.middleware.cors import CORSMiddleware

from exceptions.error_handlers import (
    custom_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from exceptions.exceptions import CustomException
from routers.auth_router import router as auth_router
from routers.comment_router import router as comment_router
from routers.payment_router import router as payment_router
from routers.user_router import router as user_router

app = FastAPI(default_response_class=ORJSONResponse) 


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


app.include_router(user_router)
app.include_router(payment_router)
app.include_router(comment_router)
app.include_router(auth_router)
