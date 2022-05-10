from irdl.models.pynamodb import LocationModel


LocationModel.set_table_name(table_name='irdl-location-test')
print(LocationModel)
if LocationModel.exists():
    print(f'table {LocationModel.Meta.table_name} already exists')
else:
    LocationModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
