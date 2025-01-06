import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from src.dominio.processamento.entidade import ClassificadorTexto
from src.infra.log import setup_logging
from src.infra.s3 import S3Handler
from src.utils.arquivos import zipar_arquivos

logger = setup_logging()

scheduler = BackgroundScheduler(timezone=pytz.UTC)

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")


def treinar_modelo() -> None:
    classificador = ClassificadorTexto()
    classificador.treinar_modelo()
    classificador.salvar_modelo()

    logger.info("Modelo treinado com sucesso!")


def backup_modelo():
    static = f"{os.getenv('RAILWAY_VOLUME_MOUNT_PATH')}/static"
    s3 = S3Handler(ACCESS_KEY, SECRET_ACCESS_KEY, "us-east-2")
    s3_key = f"{datetime.now().strftime('YYYY-MM-DD')}.zip"
    arquivos_para_zipar = [
        f"{static}/dados_categorizados.csv",
        f"{static}/classifier.joblib",
        f"{static}/vectorizer.joblib",
    ]

    arquivo_zipado = zipar_arquivos(arquivos_para_zipar)

    s3.upload_file(arquivo_zipado, "model-backup")

    logger.info(f"Backup {s3_key} realizado com sucesso!")


async def iniciar_scheduler() -> None:
    s3 = S3Handler(ACCESS_KEY, SECRET_ACCESS_KEY, "us-east-2")
    existe_backup = s3.list_files("caderneta-prod", "model-backup")

    scheduler.add_job(
        treinar_modelo,
        trigger=CronTrigger(hour=3),
        id="treina_modelo",
        name="Treinamento Modelo Transação",
        replace_existing=True,
    )

    scheduler.add_job(
        backup_modelo,
        trigger=CronTrigger(hour=4),
        id="model_backup",
        name="Backup do modelo de ML",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler iniciado com sucesso")


@asynccontextmanager
async def iniciar_servicos(app: FastAPI) -> AsyncGenerator:
    await iniciar_scheduler()
    yield
