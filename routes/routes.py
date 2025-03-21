from resources.UserResource import RegisterResource
from resources.CRMResource import ListCRMObjects


def initialize_routes(api):
    api.add_resource(RegisterResource, '/api/register')
    api.add_resource(ListCRMObjects, '/api/new-crm-objects')
