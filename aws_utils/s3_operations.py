from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import uuid
import logging


from common.configs.config import config as cfg


def generate_bucket_key(content_type):
    time_stamp = int(datetime.now().timestamp())
    extension = content_type.split("/")[1]
    return f"image-{uuid.uuid4()}-{str(time_stamp)}.{extension}"


def generate_presigned_url(bucket_key, content_type):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=cfg.get("aws", "AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=cfg.get("aws", "AWS_SECRET_ACCESS_KEY"),
        region_name=cfg.get("aws", "AWS_DEFAULT_REGION"),
    )
    try:
        pre_signed_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": cfg.get("aws", "AWS_BUCKET_NAME"),
                "Key": bucket_key,
                "ContentType": content_type,
            },
            ExpiresIn=cfg.get("aws", "AWS_EXPIRATION"),
        )
        return pre_signed_url
    except ClientError as err:
        logging.error(f"Generating presigned url: {err}", exc_info=True)
        return None
