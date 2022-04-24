import os
from typing import List

from ..base import BaseStorageRepository
from ....aws.resource import S3 as S3_resource
from ....settings import settings
from ....utils.logger import Logger


class BaseS3Repository(BaseStorageRepository):

    def __init__(self, bucket_name: str = settings.S3_BUCKET_NAME):
        super().__init__()
        self._bucket_name = bucket_name
        try:
            S3_resource.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': settings.AWS_REGION_NAME
                },
            )
            Logger.w('S3', f'created bucket [{bucket_name}]')
        except S3_resource.meta.client.exceptions.BucketAlreadyOwnedByYou as e:
            Logger.w('S3', f'bucket [{bucket_name}] already exists')
        self._bucket = S3_resource.Bucket(bucket_name)

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
    ) -> str:
        s3_prefix = f's3://{self._bucket_name}/'
        filepath = s3_filepath.replace(s3_prefix, '')
        object = self._bucket.Object(filepath)
        object.download_file(local_filepath)

        return local_filepath

    def get_filelist(
        self,
        basedir: str,
        marker: str = '',
    ) -> List[str]:
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
            ) for file in files]

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
