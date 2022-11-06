import os

from irdl.services.device_management import OrganizationManager

om = OrganizationManager()

om.cleanup_all_resources(
    organization_name=os.environ['AWS_COGNITO_TEST_ORGANIZATION_USERNAME'],
)
