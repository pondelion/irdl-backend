from irdl.models.pynamodb.location import LocationModel, LocalLocationModel

# location = LocationModel.get('android_test_device1', '2022-03-19 12:01:30')
# print(location.attribute_values)

# if not LocalLocationModel.exists():
#     LocalLocationModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
# print(LocalLocationModel(**location.attribute_values).save())

# locations = LocationModel.query('android_test_device1')
# print([l.attribute_values for l in locations])

# locations = LocationModel.query('android_test_device1', LocationModel.datetime > '2022-03-19 12:26:17')
# print([l.attribute_values for l in locations])

# locations = LocationModel.query('android_test_device1', filter_condition=(LocationModel.lat > 20.0))
# print([l.attribute_values for l in locations])

# locations = LocationModel.query(
#     'android_test_device1',
#     LocationModel.datetime > '2022-03-19 12:26:17',
#     filter_condition=(LocationModel.lat > 20.0) & (LocationModel.lng > 20.0)
# )
# print([l.attribute_values for l in locations])


locations = LocationModel.query(
    'android_test_device1',
    scan_index_forward=False,
    limit=1,
)
print([l.attribute_values for l in locations])

locations = LocationModel.query(
    'android_test_device1',
    scan_index_forward=True,
    limit=1,
)
print([l.attribute_values for l in locations])
