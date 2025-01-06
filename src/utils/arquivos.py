import os
import zipfile
from datetime import datetime
from io import BytesIO


def zipar_arquivos(files_to_zip):
    memory_zip = BytesIO()

    with zipfile.ZipFile(memory_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
            else:
                print(f"Warning: File not found - {file_path}")

    memory_zip.seek(0)
    return memory_zip
