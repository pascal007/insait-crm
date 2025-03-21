from flask import request
from flask_restful import Resource

from resources.UserResource import hubspot


class ListCRMObjects(Resource):

    @staticmethod
    def get():
        created_after = request.args.get("created_after")
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        contacts = hubspot.get_new_contacts(created_after, limit, offset)
        deals = hubspot.get_new_deals(created_after, limit, offset)
        tickets = hubspot.get_new_tickets(created_after, limit, offset)
        return {"contacts": contacts, "deals": deals, "tickets": tickets}
