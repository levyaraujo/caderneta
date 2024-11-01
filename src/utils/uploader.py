import os

import dotenv

dotenv.load_dotenv()

BUCKET = os.getenv("BUCKET", "development")


class Uploader:
    def __init__(self):
        self.bucket = BUCKET

    def upload_file(self, object_key: str, arquivo: bytes):
        caminho_completo = os.path.join(self.bucket, object_key)

        os.makedirs(self.bucket, exist_ok=True)
        with open(caminho_completo, "wb") as f:
            f.write(arquivo)

        print(caminho_completo)
        return caminho_completo
