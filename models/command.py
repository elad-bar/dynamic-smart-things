import logging

from helpers.command_validators import ARGUMENT_VALIDATORS
from helpers.errors import CommandError

_LOGGER = logging.getLogger(__name__)


class CommandEntity:
    def __init__(self):
        self.command: str | None = None
        self.arguments: list[dict] | None = None

    def validate_command(self, args: list | None = None):
        expected_args = len(self.arguments)
        received_args = 0 if args is None else len(args)

        if expected_args != received_args:
            error_message = (
                f"Command was expecting {expected_args} argument, "
                f"{received_args} were received"
            )

            raise CommandError(error_message)

        for i in range(0, received_args):
            arg_data = self.arguments[i]
            arg_input = args[i]

            schema = arg_data.get("schema", {})
            arg_name = arg_data.get("name")

            arg_type = schema.get("type")

            validate = ARGUMENT_VALIDATORS.get(arg_type)

            if validate is not None:
                validate(arg_name, schema, arg_input)

    @staticmethod
    def load(data: dict):
        _LOGGER.debug(f"Loading command, Data: {data}")

        entity = CommandEntity()
        entity.command = data.get("command")
        entity.arguments = data.get("arguments")

        return entity
