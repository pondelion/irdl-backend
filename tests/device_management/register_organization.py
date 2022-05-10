from ast import Or
from irdl.services.device_management import OrganizationManager


om = OrganizationManager()


res = om.create_organization(
    organization_name='test_organization',
    mail_address='**********@gmail.com',
    password='Test@pswd',
)
print(res)
