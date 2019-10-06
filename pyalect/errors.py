class UsageError(Exception):
    def __init__(self, message):
        if isinstance(message, Exception):
            self._type = type(message)
        else:
            self._type = type(self)
        super().__init__(str(message))

    def __str__(self):
        return f"{self._type.__name__}: {super().__str__()}"
