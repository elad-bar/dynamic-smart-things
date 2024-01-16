
class CommandError(Exception):
    def __init__(self,
                 error_message: str
                 ):
        self.message = error_message
