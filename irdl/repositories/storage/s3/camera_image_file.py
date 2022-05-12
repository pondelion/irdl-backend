from .s3 import RemoteS3Repository, LocalS3Repository


class CameraImageFileRemoteRepository(RemoteS3Repository):
    pass


class CameraImageFileLocalRepository(LocalS3Repository):
    pass
