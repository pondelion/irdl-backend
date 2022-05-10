import os

from irdl.services.device_management import OrganizationManager


om = OrganizationManager()

om.create_organization(
    organization_name=os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME'],
    mail_address='test_organization@asldksa.com',
    password=os.environ['AWS_COGNITO_TEST_ORGANIZATION_PASSWORD']
)
