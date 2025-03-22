import os

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from uuid import uuid4


def upload_to_s3(local_file_path, bucket_name, s3_key=None):
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")

    if s3_key is None:
        s3_key = str(uuid4()) + os.path.basename(local_file_path)

    s3_client = boto3.client("s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY)

    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_key)
        print(f"Upload successful: {s3_key} to bucket {bucket_name}")
        return True
    except FileNotFoundError:
        print(f"The file {local_file_path} was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except ClientError as e:
        print(f"S3 error: {e}")
        return False
