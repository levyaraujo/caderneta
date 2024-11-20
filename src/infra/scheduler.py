from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime
import pytz
from fastapi import FastAPI

from src.dominio.processamento.entidade import ClassificadorTexto

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y %H:%M",
)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=pytz.UTC)


def treinar_modelo():
    classificador = ClassificadorTexto()
    classificador.treinar_modelo()
    classificador.salvar_modelo()
    return


@asynccontextmanager
async def iniciar_scheduler(app: FastAPI):
    scheduler.add_job(
        treinar_modelo,
        trigger=CronTrigger(hour=6),  # Isso será executado 3h da manhã em UTC-3
        id="treina_modelo",
        name="Treinamento Modelo Transação",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler iniciado com sucesso")
    yield
