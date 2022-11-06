import os
from time import sleep
from typing import List, Optional

from ....aws.resource import S3 as S3_resource
from ....aws.resource_local import S3_LOCAL as S3_resource_local
from ....settings import settings
from ....utils.logger import Logger
from ..base import BaseStorageRepository


class BaseS3Repository(BaseStorageRepository):

    def __init__(
        self,
        s3_resource,
        bucket_name: str = settings.S3_BUCKET_NAME,
    ):
        super().__init__()
        self._bucket_name = bucket_name
        try:
            s3_resource.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': settings.AWS_REGION_NAME
                },
            )
            Logger.w('S3', f'created bucket [{bucket_name}]')
        except s3_resource.meta.client.exceptions.BucketAlreadyOwnedByYou:
            Logger.w('S3', f'bucket [{bucket_name}] already exists')
        self._bucket = s3_resource.Bucket(bucket_name)

    def save(
        self,
        local_filepath: str,
        s3_filepath: str,
    ) -> None:
        if s3_filepath.startswith('s3://'):
            s3_filepath = s3_filepath.replace(f's3://{self._bucket_name}/', '')

        self._bucket.upload_file(
            local_filepath,
            s3_filepath
        )

    def get(
        self,
        s3_filepath: str,
        local_filepath: str,
        n_retry: int = 1,
        retry_interval_sec: float = 1.0,
    ) -> Optional[str]:
        s3_prefix = f's3://{self._bucket_name}/'
        filepath = s3_filepath.replace(s3_prefix, '')
        success = None
        while success is None and n_retry > 0:
            try:
                object = self._bucket.Object(filepath)
                object.download_file(local_filepath)
                success = local_filepath
            except Exception as e:
                print(e)
                sleep(retry_interval_sec)
            n_retry = n_retry - 1
        return success

    def get_filelist(
        self,
        basedir: str,
        marker: str = '',
    ) -> List[str]:
        s3_prefix = f's3://{self._bucket_name}/'
        basedir = basedir.replace(s3_prefix, '')
        if basedir.startswith('/'):
            basedir = basedir[1:]

        objs = self._bucket.meta.client.list_objects(
            Bucket=self._bucket.name,
            Prefix=basedir if basedir[-1] == '/' else basedir + '/',
            Marker=marker,
        )

        s3_prefix = f's3://{self._bucket_name}/'
        s3_filelist = []

        while 'Contents' in objs:
            files = [o.get('Key') for o in objs.get('Contents')]

            s3_paths = [os.path.join(
                s3_prefix,
                file,
            ) for file in files if not file.endswith('/')]

            s3_filelist += s3_paths

            if 'IsTruncated' in objs:
                marker = files[-1]
                objs = self._bucket.meta.client.list_objects(
                    Bucket=self._bucket.name,
                    Prefix=basedir if basedir[-1] == '/' else basedir + '/',
                    Marker=marker,
                )
            else:
                break

        return s3_filelist


class LocalS3Repository(BaseS3Repository):

    def __init__(
        self,
        s3_resource = S3_resource_local,
        bucket_name: str = settings.S3_BUCKET_NAME,
    ):
        super().__init__(s3_resource, bucket_name)


class RemoteS3Repository(BaseS3Repository):

    def __init__(
        self,
        s3_resource = S3_resource,
        bucket_name: str = settings.S3_BUCKET_NAME,
    ):
        super().__init__(s3_resource, bucket_name)
