from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import uuid
import json
import os


# Allowed file extensions and max file size (10MB)
ALLOWED_EXTENSIONS = {".jpeg", ".jpg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename: str) -> bool:
    """
    Check if the file has an allowed extension.
    """
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


# Initialize MinIO client
# i should have used an environment variable for the access key and secret key but this is for easirer testability for you guys
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

BUCKET_NAME = "labelbox"


def ensure_bucket_exists(bucket_name: str):
    """
    Ensure the specified bucket exists, and set it to public.
    """
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        
        # Set bucket policy to public
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }
            ]
        }
        policy_json = json.dumps(policy)
        minio_client.set_bucket_policy(bucket_name, policy_json)
        print(f"Public policy applied to bucket '{bucket_name}'.")
    except S3Error as e:
        print(f"Error ensuring bucket '{bucket_name}': {e}")


# Ensure the bucket exists
ensure_bucket_exists(BUCKET_NAME)


def upload_file_to_minio(file: UploadFile):
    """
    Upload a file to MinIO and return the file's public URL.
    """
    try:
        # Check file type
        if not allowed_file(file.filename):
            raise ValueError("File type not allowed. Allowed types are: " + ", ".join(ALLOWED_EXTENSIONS))

        # Check file size
        file.file.seek(0, os.SEEK_END)  # Move pointer to end of file to get size
        file_size = file.file.tell()
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds the maximum limit of {MAX_FILE_SIZE // (1024 * 1024)} MB.")

        # Reset file pointer after size check
        file.file.seek(0)

        # Generate unique file name
        file_name = f"{uuid.uuid4()}-{file.filename}"
        minio_client.put_object(
            BUCKET_NAME,
            file_name,
            file.file,
            length=file_size,
            part_size=10 * 1024 * 1024,  # 10MB part size
            content_type=file.content_type
        )
        return f"http://localhost:9000/{BUCKET_NAME}/{file_name}"

    except ValueError as ve:
        raise RuntimeError(f"Validation Error: {ve}")
    except Exception as e:
        raise RuntimeError(f"Failed to upload file: {e}")
