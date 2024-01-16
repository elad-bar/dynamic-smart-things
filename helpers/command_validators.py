from helpers.errors import CommandError


def _validate_array(name, schema, value):
    items = schema.get("items")
    arg_type = items.get("type")

    validate = ARGUMENT_VALIDATORS.get(arg_type)

    if validate is not None:
        validate(name, items, value)


def _validate_boolean(name, _schema, value):
    if not isinstance(value, bool):
        error_message = (
            f"Argument {name} [{value}] should be boolean [true, false]"
        )

        raise CommandError(error_message)


def _validate_integer(name, schema, value):
    arg_min = schema.get("minimum", schema.get("min"))
    arg_max = schema.get("maximum", schema.get("max"))

    value = int(value)

    if arg_min is not None and arg_max is not None:
        if not arg_max >= value >= arg_min:
            error_message = (
                f"Argument {name} [{value}] should be between {arg_min} and {arg_max}"
            )

            raise CommandError(error_message)


def _validate_string(name, schema, value):
    arg_enum = schema.get("enum")
    arg_max_length = schema.get("maxLength")

    if arg_enum:
        if value not in arg_enum:
            error_message = (
                f"Argument {name} [{value}] should be one of {arg_enum}"
            )

            raise CommandError(error_message)

    if arg_max_length:
        if len(str) > arg_max_length:
            error_message = (
                f"Argument {name} [{value}] should be up to {arg_max_length} characters"
            )

            raise CommandError(error_message)


ARGUMENT_VALIDATORS = {
    "integer": _validate_integer,
    "number": _validate_integer,
    "string": _validate_string,
    "boolean": _validate_boolean,
    "array": _validate_array
}
