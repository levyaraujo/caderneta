from fastapi import FastAPI

from src.dominio.bot.resources import BotRouter

app = FastAPI()
app.include_router(BotRouter)
