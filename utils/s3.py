import boto3

s3_client = boto3.client("s3")


def list_s3_files(bucket, prefix, suffix=None):
    paginator = s3_client.get_paginator("list_objects_v2")
    files = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not suffix or key.endswith(suffix):
                files.append(key)
    return files


def build_s3_url(key):
    from studious_octo_funicular_ui.constants import S3_BASE_URL

    return f"{S3_BASE_URL}/{key}"
