from cerberus import Validator


class ValidatorException(Exception):
    pass


def validate_args(data, validator):
    if not validator.validate(data):
        raise ValidatorException(
            "Invalid arguments ({})".format(validator.errors)
        )


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
read_entity_comments_validator = Validator(
    allow_unknown=False,
    schema={
        "type": {"type": "string", "required": True},
        "entity": {"type": "string", "required": True},
        "limit": {"type": "string", "required": False},
        "offset": {"type": "string", "required": False}
    })
read_entity_replies_validator = read_entity_comments_validator
read_user_comments_validator = Validator(
    allow_unknown=False,
    schema={
        "user_token": {"type": "string", "required": True}
    })
read_comment_replies_validator = Validator(
    allow_unknown=False,
    schema={
        "comment_token": {"type": "string", "required": True}
    })
