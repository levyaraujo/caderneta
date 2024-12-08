from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from src.dominio.processamento.entidade import ClassificadorTexto
from src.infra.log import setup_logging

logger = setup_logging()

scheduler = BackgroundScheduler(timezone=pytz.UTC)


def treinar_modelo() -> None:
    classificador = ClassificadorTexto()
    classificador.treinar_modelo()
    classificador.salvar_modelo()

    logger.info("Modelo treinado com sucesso!")


async def iniciar_scheduler() -> None:
    scheduler.add_job(
        treinar_modelo,
        trigger=CronTrigger(hour=3),
        id="treina_modelo",
        name="Treinamento Modelo Transação",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler iniciado com sucesso")


@asynccontextmanager
async def iniciar_servicos(app: FastAPI) -> AsyncGenerator:
    await iniciar_scheduler()
    yield
