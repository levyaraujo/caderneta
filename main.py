import os

import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.infra.middlewares.whatsapp import WhatsAppOnboardMiddleware
from src.dominio.bot.resources import BotRouter
from src.dominio.usuario.resources import UsuarioRouter
from src.infra.middlewares.twilio import TwilioOnboardMiddleware

BUCKET = os.getenv("BUCKET")
app = FastAPI()


sentry_sdk.init(
    dsn="https://9e11244046c4b957853cc51bd10a478b@o4508257512521728.ingest.us.sentry.io/4508257514618880",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=0.5,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)

app.mount("/static", StaticFiles(directory=BUCKET), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(WhatsAppOnboardMiddleware)
app.add_middleware(TwilioOnboardMiddleware)

app.include_router(BotRouter)
app.include_router(UsuarioRouter)
