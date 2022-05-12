from irdl.models.pynamodb import ObjectDetectionResultModel

# od_results = ObjectDetectionResultModel.query(hash_key='android_test_device1')
# print([r.attribute_values for r in od_results])

od_results = ObjectDetectionResultModel.query(
    hash_key='android_test_device1',
    filter_condition=ObjectDetectionResultModel.datetime >= '2022-04-29T16:59:23.057203+00:00'
)
print([r.attribute_values for r in od_results])