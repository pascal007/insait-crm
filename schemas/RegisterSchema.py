from marshmallow import Schema, fields, validates, ValidationError


class DealSchema(Schema):
    dealname = fields.String(required=True)
    amount = fields.Float(required=True)
    dealstage = fields.String(required=True)


class TicketSchema(Schema):
    subject = fields.String(required=True)
    description = fields.String(required=True)
    category = fields.String(
        required=True,
        validate=lambda x: x in ["general_inquiry", "technical_issue", "billing", "service_request", "meeting"]
    )
    pipeline = fields.String(required=True)
    hs_ticket_priority = fields.String(required=True)
    hs_pipeline_stage = fields.Integer(required=True)

    @validates("hs_pipeline_stage")
    def validate_pipeline_stage(self, value):
        if value not in range(1, 5):
            raise ValidationError("hs_pipeline_stage must be an integer between 1 and 4.")

    @validates("hs_ticket_priority")
    def validate_ticket_priority(self, value):
        allowed_values = {"LOW", "MEDIUM", "HIGH", "URGENT"}
        if value not in allowed_values:
            raise ValidationError(f"hs_ticket_priority must be one of {allowed_values}.")


class RegisterSchema(Schema):
    firstname = fields.String(required=True)
    lastname = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)
    deals = fields.List(fields.Nested(DealSchema), required=True, validate=lambda x: len(x) > 0)
    tickets = fields.List(fields.Nested(TicketSchema), required=True, validate=lambda x: len(x) > 0)

    @validates("phone")
    def validate_phone(self, value):
        if not value.isdigit() or len(value) not in [10, 11]:
            raise ValidationError("Invalid phone number format. Must be 10 or 11 digits.")
