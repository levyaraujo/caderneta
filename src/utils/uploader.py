import os

import dotenv

dotenv.load_dotenv()

BUCKET = os.getenv("BUCKET", "/opt/caderneta/static")
STATIC_URL = os.getenv("STATIC_URL")


class Uploader:
    def __init__(self):
        self.bucket = BUCKET

    def upload_file(self, object_key: str, arquivo: bytes):
        caminho_completo = os.path.join(self.bucket, object_key)  # noqa

        os.makedirs(self.bucket, exist_ok=True)
        with open(caminho_completo, "wb") as f:
            f.write(arquivo)

        return f"{STATIC_URL}/{object_key}"
