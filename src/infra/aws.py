from io import BytesIO

import boto3
from botocore.exceptions import ClientError
from typing import Dict, Optional, Union, BinaryIO
import logging
import mimetypes
import os


class S3Uploader:
    """
    Gerencia uploads de arquivos e acesso a objetos no AWS S3 usando URLs pré-assinadas.
    """

    def __init__(
        self,
        bucket_name: str,
        aws_region: str = "sa-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        """
        Inicializa o S3Uploader com credenciais e configurações AWS.

        Argumentos:
            bucket_name: Nome do bucket S3
            aws_region: Região AWS (padrão: us-east-1)
            aws_access_key_id: ID da chave de acesso AWS (opcional se usar roles IAM)
            aws_secret_access_key: Chave de acesso secreta AWS (opcional se usar roles IAM)
        """
        self.bucket_name = bucket_name
        self.region = aws_region

        self.s3_client = boto3.client(
            "s3",
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        self.logger = logging.getLogger(__name__)

    def upload_file(
        self,
        file_bytes: Union[bytes, BinaryIO, BytesIO],
        object_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None,
        extra_args: Optional[Dict] = None,
    ) -> bool:
        """
        Faz upload direto de bytes para o S3.

        Argumentos:
            file_bytes: Dados do arquivo em bytes ou objeto tipo arquivo binário
            object_key: Chave do objeto no S3 (caminho/nome.extensao)
            content_type: Tipo de conteúdo do arquivo (ex: 'image/jpeg')
            metadata: Dicionário com metadados para anexar ao objeto
            extra_args: Argumentos adicionais para o upload

        Retorna:
            bool: True se o upload foi bem sucedido, False caso contrário
        """
        try:
            # Prepara os argumentos extras
            upload_args = extra_args or {}

            # Adiciona content type se fornecido
            if content_type:
                upload_args["ContentType"] = content_type
            # Tenta adivinhar content type pelo nome do arquivo se não fornecido
            elif "ContentType" not in upload_args:
                guessed_type, _ = mimetypes.guess_type(object_key)
                if guessed_type:
                    upload_args["ContentType"] = guessed_type

            # Adiciona metadados se fornecidos
            if metadata:
                upload_args["Metadata"] = metadata

            # Converte para BytesIO se necessário
            if isinstance(file_bytes, bytes):
                file_bytes = BytesIO(file_bytes)

            # Faz o upload
            self.s3_client.upload_fileobj(
                file_bytes, self.bucket_name, object_key, ExtraArgs=upload_args
            )

            return True

        except ClientError as e:
            self.logger.error(f"Erro no upload de bytes para S3: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado no upload: {e}")
            return False
