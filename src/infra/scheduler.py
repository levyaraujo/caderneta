import sys
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import pytz
from fastapi import FastAPI

from src.dominio.processamento.entidade import ClassificadorTexto
from src.infra.log import setup_logging
from src.infra.migration import run_migrations

logger = setup_logging()

scheduler = BackgroundScheduler(timezone=pytz.UTC)


def treinar_modelo():
    classificador = ClassificadorTexto()
    classificador.treinar_modelo()
    classificador.salvar_modelo()
    return


async def iniciar_scheduler():
    scheduler.add_job(
        treinar_modelo,
        trigger=CronTrigger(hour=6),  # Isso será executado 3h da manhã em UTC-3
        id="treina_modelo",
        name="Treinamento Modelo Transação",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler iniciado com sucesso")


@asynccontextmanager
async def iniciar_servicos(app: FastAPI):
    await iniciar_scheduler()
    yield
