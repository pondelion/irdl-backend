from irdl.models.pynamodb.location import LocationModel, LocalLocationModel

location = LocationModel.get('android_test_device1', '2022-03-19 12:01:30')
print(location.attribute_values)

if not LocalLocationModel.exists():
    LocalLocationModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
print(LocalLocationModel(**location.attribute_values).save())

# locations = LocationModel.query('android_test_device1')
# print([l.attribute_values for l in locations])