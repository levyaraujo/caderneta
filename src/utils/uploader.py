import os

import dotenv

dotenv.load_dotenv()

BUCKET = os.getenv("BUCKET")
STATIC_URL = os.getenv("STATIC_URL")


class Uploader:
    def __init__(self):
        os.makedirs(BUCKET, exist_ok=True)

    def upload_file(self, object_key: str, arquivo: bytes):
        caminho_completo = os.path.join(BUCKET, object_key)  # noqa

        os.makedirs(BUCKET, exist_ok=True)
        with open(caminho_completo, "wb") as f:
            f.write(arquivo)

        return f"{STATIC_URL}/{object_key}"
