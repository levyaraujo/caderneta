from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from src.dominio.bot.resources import BotRouter
from src.dominio.usuario.resources import UsuarioRouter
from src.infra.middlewares.onboard import UserOnboardMiddleware
import os

BUCKET = os.getenv("BUCKET")

origins = [
    "https://caderneta.tunn.dev",
    "http://localhost",
    "http://localhost:5173",
]

app = FastAPI()

app.mount("/static", StaticFiles(directory=BUCKET), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(UserOnboardMiddleware)

app.include_router(BotRouter)
app.include_router(UsuarioRouter)


@app.middleware("http")
async def add_custom_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.middleware("http")
async def debug_cors(request, call_next):
    response = await call_next(request)
    print("Request Headers:", request.headers)
    print("Response Headers:", response.headers)
    return response
