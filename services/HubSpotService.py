import os
import time

import requests
from dotenv import load_dotenv

from exceptions.CRMException import CRMError
from interface.CRMStrategy import CRMStrategyInterface
from logger_config import logger

load_dotenv()


class HubSpotCRMService(CRMStrategyInterface):
    HUBSPOT_BASE_URL = os.environ.get('HUBSPOT_BASE_URL')
    HUBSPOT_TOKEN_URL = os.environ.get('HUBSPOT_TOKEN_URL')
    CONTACT_VERIFY_URL = HUBSPOT_BASE_URL + "/crm/v3/objects/contacts/{}?idProperty=email"
    CONTACT_CREATE_URL = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts"
    DEAL_PIPELINE_URL = HUBSPOT_BASE_URL + '/crm/v3/pipelines/deals'
    DEAL_CREATE_URL = HUBSPOT_BASE_URL + '/crm/v3/objects/deals'
    DEAL_RETRIEVE_URL = HUBSPOT_BASE_URL + '/crm/v3/associations/contacts/deals/{}'
    DEAL_LIST_URL = HUBSPOT_BASE_URL + '/crm/v3/objects/deals'
    TICKET_LIST_URL = HUBSPOT_BASE_URL + '/crm/v3/objects/tickets'

    def __init__(self):
        self.access_token = None
        self.token_expires_at = 0

    def _get_access_token(self):
        current_time = time.time()
        if current_time < self.token_expires_at:
            logger.info("Existing access token still valid")
            return self.access_token
        data = {
            "grant_type": "refresh_token",
            "client_id": os.environ.get('HUBSPOT_CLIENT_ID'),
            "client_secret": os.environ.get('HUBSPOT_CLIENT_SECRET'),
            "refresh_token": os.environ.get('HUBSPOT_REFRESH_TOKEN')
        }
        response = self._make_request(self.HUBSPOT_TOKEN_URL, "POST", data=data)
        if response.status_code == 200:
            logger.info("Existing access token invalid, obtaining new access token")
            response_data = response.json()
            self.access_token = response_data.get("access_token")
            self.token_expires_at = time.time() + response_data.get("expires_in")
            return self.access_token
        logger.error(f"Error retrieving access token, {response.status_code}")
        raise CRMError('Error retrieving access token')

    def _get_headers(self):
        return {"Authorization": f"Bearer {self._get_access_token()}", "Content-Type": "application/json"}

    def _retrieve_existing_contact_data(self, email):
        response = self._make_request(self.CONTACT_VERIFY_URL.format(email), "GET", headers=self._get_headers())
        if response.status_code == 200:
            logger.info(f"Exiting user with {email} exists for update")
            return True, response.json()
        elif response.status_code == 404:
            return False, None
        logger.info('Invalid response code response from contact check')
        raise CRMError('Invalid response from provider')

    def _validate_and_clean_deal_data(self, deal_data):
        deal_results = self._make_request(self.DEAL_PIPELINE_URL, "GET", headers=self._get_headers()).json()['results']
        if not deal_results:
            logger.error("deal pipeline stages not configured ")
            raise CRMError("Deal pipeline stages not configured")
        deal_pipeline_data = deal_results[0]
        deal_pipeline_id = deal_pipeline_data['id']
        deal_pipeline_stages_data = {data["label"]: data["id"] for data in deal_pipeline_data['stages']}

        for deal in deal_data:
            if not deal_pipeline_stages_data.get(deal['dealstage']):
                logger.error("Invalid deal stage submitted")
                raise CRMError(
                    f"Invalid deal stage submitted, valid stages are {', '.join(deal_pipeline_stages_data.keys())}")
            deal['dealstage'] = deal_pipeline_stages_data.get(deal['dealstage'])
        return deal_data, deal_pipeline_id

    def _make_request(self, url, method, max_retries=5, backoff_factor=1, **kwargs):
        retries = 0
        backoff = backoff_factor

        while retries < max_retries:
            logger.info(f"making api call to {url} using {method} method")
            response = requests.request(method, url, **kwargs)

            if response.status_code == 429:
                print(f"Rate limited. Retrying in {backoff} seconds...")
                time.sleep(backoff)
                backoff *= 2
                retries += 1
            else:
                return response
        logger.error("Max retries reached, request failed.")
        raise CRMError("Max retries reached, request failed.")

    def create_or_update_contact(self, email, validated_data):
        is_existing, data = self._retrieve_existing_contact_data(email)
        tickets_data = validated_data.pop('tickets')
        deal_data, deal_pipeline_id = self._validate_and_clean_deal_data(validated_data.pop("deals", []))
        if is_existing:
            contact_id = data['id']
            logger.info(f"Exiting user with {email} exists for update")
            response = self._make_request(
                self.CONTACT_VERIFY_URL.format(email),
                'PATCH',
                headers=self._get_headers(),
                json={"properties": validated_data}
            )
            if response.status_code == 200:
                deal_ids = self.create_or_update_deal(contact_id, deal_data, deal_pipeline_id)
                logger.info(f"User with {email} updated successfully")
                self.create_support_ticket(contact_id, deal_ids, tickets_data)
                return response.json()
            else:
                logger.info(f"{str(response.status_code)}: Error updating user with email {email}."
                            f"{response.json()}")
                raise CRMError("Error during update on user")
        else:
            data = {
                "properties": {
                    "firstname": validated_data.get("firstname"),
                    "lastname": validated_data.get("lastname"),
                    "email": email,
                    "phone": validated_data.get("phone"),
                    "company": os.environ.get("ORGANIZATION_NAME")
                }
            }
            response = self._make_request(
                self.CONTACT_CREATE_URL, "POST", headers=self._get_headers(), json=data)
            if response.status_code == 201:
                logger.info("Contact created successfully")
                contact_id = response.json()['id']
                deal_ids = self.create_or_update_deal(contact_id, deal_data, deal_pipeline_id)
                self.create_support_ticket(contact_id, deal_ids, tickets_data)
                return response.json()
            raise CRMError("Error during creation of user")

    # def _validate_and_create_field_for_deal(self, field_name):
    #     data = {
    #         "name": field_name,
    #         "label": field_name,
    #         "type": "string",
    #         "fieldType": "text",
    #         "groupName": "dealinformation",
    #         "formField": False
    #     }
    #     response = requests.get(
    #     "https://api.hubapi.com/crm/v3/properties/deals", headers=self._get_headers(), json=data)
    #     if response.status_code == 200:
    #         pass
    #     response = requests.post(
    #     f"{self.HUBSPOT_BASE_URL}/crm/v3/properties/deals", headers=self._get_headers(), json=data)

    def _validate_and_create_field_for_ticket(self, ticket):
        response = self._make_request(
            self.HUBSPOT_BASE_URL + "/crm/v3/properties/tickets",
            'GET',
            headers=self._get_headers()
        )
        if response.status_code == 200:
            ticket_fields = [field['name'] for field in response.json()['results']]
            for ticket_field in ticket:
                if ticket_field not in ticket_fields:
                    data = {
                        "name": ticket_field,
                        "label": ticket_field,
                        "type": "string",
                        "fieldType": "text",
                        "groupName": "ticketinformation",
                        "options": [],
                    }
                    response = self._make_request(
                        self.HUBSPOT_BASE_URL + '/crm/v3/properties/tickets', method='POST',
                        headers=self._get_headers(), json=data
                    )
                    if response.status_code == 201:
                        logger.info(f"successfully created field {ticket_field} for ticket")
                    else:
                        raise CRMError(f'Error creating field for ticket {ticket_field}')
        else:
            logger.error(f"Error: {response.status_code}, {response.text}")
            raise CRMError('Error updating ticket fields')

    def create_or_update_deal(self, contact_id, deals_data, deal_pipeline_id):
        deal_ids = set()
        data = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "contact_id",
                            "operator": "EQ",
                            "value": contact_id
                        }
                    ]
                }
            ],
            "properties": ["dealname", "amount", "dealstage", "contact_id"]
        }

        url = f"{self.HUBSPOT_BASE_URL}/crm/v3/objects/deals/search"
        response = self._make_request(
            url, method='POST',
            headers=self._get_headers(), json=data
        )
        existing_deals = {}
        if response.status_code == 200 and response.json():
            for deal in response.json()['results']:
                existing_deals[deal['properties']['dealname']] = deal

        for deal_data in deals_data:
            if not (deal_data.get("dealname") in existing_deals):
                deal_payload = {
                    "properties": {
                        "amount": deal_data.get("amount"),
                        "dealname": deal_data.get("dealname"),
                        "pipeline": deal_pipeline_id,
                        "dealstage": deal_data.get("dealstage"),
                        "contact_id": contact_id
                    },
                    "associations": [
                        {
                            "to": {
                                "id": contact_id
                            },
                            "types": [
                                {
                                    "associationCategory": "HUBSPOT_DEFINED",
                                    "associationTypeId": 3
                                }
                            ]
                        },
                    ]
                }
                response = self._make_request(
                    self.DEAL_CREATE_URL, method='POST',
                    headers=self._get_headers(), json=deal_payload
                )
                if response.status_code == 201:
                    deal_ids.add(response.json()['id'])
                    logger.info(f"Deal successfully created for customer {contact_id}")
            else:
                deal_id = existing_deals[deal_data['dealname']]['id']
                url = f"{self.HUBSPOT_BASE_URL}/crm/v3/objects/deals/{deal_id}"
                response = self._make_request(
                    url, method='PATCH',
                    headers=self._get_headers(), json={"properties": {
                        "amount": deal_data.get("amount"),
                        "dealname": deal_data.get("dealname"),
                        "pipeline": deal_pipeline_id,
                        "dealstage": deal_data.get("dealstage"),
                        "contact_id": contact_id
                    }}
                )
                if response.status_code == 200:
                    logger.info(f"deal update for {contact_id} successful")
                    deal_ids.add(deal_id)
        return deal_ids

    def create_support_ticket(self, contact_id, deal_ids, ticket_data):
        for ticket in ticket_data:
            url = f"{self.HUBSPOT_BASE_URL}/crm/v3/objects/tickets"
            data = {
                "properties": ticket,
                "associations": [
                    {"to": {
                        "id": contact_id},
                        "types": [
                            {"associationCategory": "HUBSPOT_DEFINED",
                             "associationTypeId": 16}
                        ]}]}
            for deal_id in deal_ids:
                data['associations'].append(
                    {"to": {
                        "id": deal_id},
                        "types": [
                            {"associationCategory": "HUBSPOT_DEFINED",
                             "associationTypeId": 28}]}
                )
            self._validate_and_create_field_for_ticket(ticket)
            response = self._make_request(url, "POST", headers=self._get_headers(), json=data)
            if response.status_code == 201:
                logger.info("Ticket successfully created")
                return response.json()
            raise CRMError(f'Error creating ticket: {response.status_code}')

    def fetch_objects(self, url, object_type, created_after=None, limit=50, offset=0, associations=None):
        url = f"{url}/?limit={limit}&offset={offset}"
        if created_after:
            url += f"&createdAfter={created_after}"
        if associations:
            url += f"&associations={associations}"
        logger.info(f"Fetching {object_type} from {url}")
        try:
            response = self._make_request(url, "GET", headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching {object_type}: {e}")
            raise CRMError(f"Failed to fetch {object_type}")

    def get_new_contacts(self, created_after, limit=50, offset=0):
        return self.fetch_objects(
            self.CONTACT_CREATE_URL, "contacts", created_after, limit, offset, associations="deals")

    def get_new_deals(self, created_after, limit=50, offset=0):
        return self.fetch_objects(self.DEAL_LIST_URL, "deals", created_after, limit, offset)

    def get_new_tickets(self, created_after, limit=50, offset=0):
        return self.fetch_objects(self.TICKET_LIST_URL, "tickets", created_after, limit, offset)
