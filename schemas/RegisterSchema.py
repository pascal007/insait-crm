from marshmallow import Schema, fields, validates, ValidationError, validate
import re


class DealSchema(Schema):
    dealname = fields.String(required=True, validate=validate.Length(min=1, error="Deal name cannot be empty."))
    amount = fields.Float(required=True)
    dealstage = fields.String(required=True, validate=validate.Length(min=1, error="Deal stage cannot be empty."))

    @validates("amount")
    def validate_amount(self, value):
        if value < 0:
            raise ValidationError("Amount must be a positive number.")
        if round(value, 2) != value:
            raise ValidationError("Amount must have up to two decimal places.")


class TicketSchema(Schema):
    TICKET_SCHEMA_CHOICES = ["general_inquiry", "technical_issue", "billing", "service_request", "meeting"]

    subject = fields.String(required=True, validate=validate.Length(min=1, error="Subject cannot be empty."))
    description = fields.String(required=True, validate=validate.Length(min=1, error="Description cannot be empty."))
    category = fields.String(
        required=True,
        validate=validate.OneOf(
            TICKET_SCHEMA_CHOICES,
            error=f"Invalid category. Must be one of: {', '.join(TICKET_SCHEMA_CHOICES)}"
        )
    )
    pipeline = fields.String(required=True, validate=validate.Length(min=1, error="Pipeline cannot be empty."))
    hs_ticket_priority = fields.String(
        required=True,
        validate=validate.OneOf(
            ["LOW", "MEDIUM", "HIGH", "URGENT"],
            error="Invalid priority. Must be one of: LOW, MEDIUM, HIGH, URGENT."
        )
    )
    hs_pipeline_stage = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=4, error="hs_pipeline_stage must be an integer between 1 and 4.")
    )


class RegisterSchema(Schema):
    firstname = fields.String(required=True, validate=validate.Length(min=1, error="First name cannot be empty."))
    lastname = fields.String(required=True, validate=validate.Length(min=1, error="Last name cannot be empty."))
    email = fields.Email(required=True, error_messages={"invalid": "Invalid email format."})
    phone = fields.String(required=True)

    deals = fields.List(fields.Nested(DealSchema), required=True, validate=validate.Length(
        min=1, error="At least one deal is required."))
    tickets = fields.List(fields.Nested(TicketSchema), required=True, validate=validate.Length(
        min=1, error="At least one ticket is required."))

    @validates("phone")
    def validate_phone(self, value):
        if not re.fullmatch(r"\d{10,11}", value):
            raise ValidationError("Invalid phone number format. Must be 10 or 11 digits.")
