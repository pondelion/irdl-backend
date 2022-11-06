from ..models.pynamodb import (CameraImageModel, LocalCameraImageModel,
                               LocalLocationModel,
                               LocalObjectDetectionResultModel,
                               LocalSensorModel, LocationModel,
                               ObjectDetectionResultModel, SensorModel)
from ..utils import Logger


def init_dynamodb():
    # Location
    try:
        if not LocationModel.exists():
            LocationModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    except Exception as e:
        Logger.e('init_dynamodb', f'Failed to create dynamodb location table.: {e}')
    # try:
    #     if not LocalLocationModel.exists():
    #         LocalLocationModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    # except Exception as e:
    #     Logger.w('init_dynamodb', f'Failed to create local dynamodb location table. : {e}')
    # Sensor
    try:
        if not SensorModel.exists():
            SensorModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    except Exception as e:
        Logger.e('init_dynamodb', f'Failed to create dynamodb sensor table. : {e}')
    # try:
    #     if not LocalSensorModel.exists():
    #         LocalSensorModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    # except Exception as e:
    #     Logger.w('init_dynamodb', f'Failed to create local dynamodb sensor table. : {e}')
    # Camera Image
    try:
        if not CameraImageModel.exists():
            CameraImageModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    except Exception as e:
        Logger.e('init_dynamodb', f'Failed to create dynamodb camera image table. : {e}')
    # try:
    #     if not LocalCameraImageModel.exists():
    #         LocalCameraImageModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    # except Exception as e:
    #     Logger.w('init_dynamodb', f'Failed to create local dynamodb camera image table. : {e}')
    # Object Detection
    try:
        if not ObjectDetectionResultModel.exists():
            ObjectDetectionResultModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    except Exception as e:
        Logger.e('init_dynamodb', f'Failed to create dynamodb object detection table. : {e}')
    # try:
    #     if not LocalObjectDetectionResultModel.exists():
    #         LocalObjectDetectionResultModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    # except Exception as e:
    #     Logger.w('init_dynamodb', f'Failed to create local dynamodb object detection table. : {e}')
