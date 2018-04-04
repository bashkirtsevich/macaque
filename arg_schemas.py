from cerberus import Validator

from app import ServerException

reply_entity_validator = Validator(
    allow_unknown=False,
    schema={
        "type": {"type": "string", "required": True},
        "entity": {"type": "string", "required": True},
        "user_token": {"type": "string", "required": True},
        "text": {"type": "string", "required": True}
    })
reply_comment_validator = Validator(
    allow_unknown=False,
    schema={
        "comment_token": {"type": "string", "required": True},
        "user_token": {"type": "string", "required": True},
        "text": {"type": "string", "required": True}
    })
edit_comment_validator = Validator(
    allow_unknown=False,
    schema={
        "user_token": {"type": "string", "required": True},
        "comment_token": {"type": "string", "required": True},
        "text": {"type": "string", "required": True}
    })
remove_comment_validator = Validator(
    allow_unknown=False,
    schema={
        "user_token": {"type": "string", "required": True},
        "comment_token": {"type": "string", "required": True}
    })
upload_comments_validator = Validator(
    allow_unknown=False,
    schema={
        "type": {"type": "string", "required": True},
        "entity": {"type": "string", "required": True}
    })


def validate_args(data, validator):
    if not validator.validate(data):
        raise ServerException(
            "Invalid arguments ({})".format(validator.errors)
        )
