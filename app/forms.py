from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    full_name = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(missing="customer", validate=validate.OneOf(["customer", "seller", "staff", "delivery"]))
