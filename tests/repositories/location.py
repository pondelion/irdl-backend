from irdl.repositories.dynamodb import LocationRepository

# repo = LocationRepository()
# records = repo.get(hash_key='android_test_device1')
# print(records)

# repo = LocationRepository()
# records = repo.get(hash_key='android_test_device_non_exists')
# print(records)

# repo = LocationRepository()
# records = repo.get_latest(device_name='android_test_device1')
# print(records)

# repo = LocationRepository()
# records = repo.get_latest(device_name='android_test_device_non_exists')
# print(records)

repo = LocationRepository()
records = repo.get_latest()
print(records)
