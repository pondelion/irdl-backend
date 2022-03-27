from ..models.pynamodb import *


def init_dynamodb():
    if not LocationModel.exists():
        LocationModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    if not LocalLocationModel.exists():
        LocalLocationModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    if not SensorModel.exists():
        SensorModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    if not LocalSensorModel.exists():
        LocalSensorModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
