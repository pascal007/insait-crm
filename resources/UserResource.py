from flask_restful import Resource
from flask import request

from exceptions.CRMException import CRMError
from schemas.RegisterSchema import RegisterSchema
from services.HubSpotService import HubSpotCRMService

from logger_config import logger

hubspot = HubSpotCRMService()


class RegisterResource(Resource):
    @staticmethod
    def post():
        """Return a hello world message
        ---
        responses:
          200:

        """
        try:
            if not request.data:
                return {'success': False, 'error': 'Payload data incomplete'}, 400
            data = request.get_json()
            validated_data = RegisterSchema().load(data=data)
            email = validated_data.pop('email')

        except Exception as e:
            return {'success': False, 'error': str(e)}, 400

        try:
            response_data = hubspot.create_or_update_contact(email, validated_data)
            return {'success': True, 'data': response_data}, 201
        except CRMError as e:
            logger.error(f"Unexpected error from Hubspot user registration: {str(e)}")
            return {'success': False, 'error': str(e)}, 503
        except Exception as e:
            logger.error(f"Unexpected error during user registration: {str(e)}")
            return {'success': False, 'error': str(e)}, 500


