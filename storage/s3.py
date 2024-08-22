from storages.backends.s3 import S3Storage

class StaticFiles(S3Storage):
    location = "static/"