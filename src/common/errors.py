class ServerException(Exception):
    def __init__(self, message="Something went wrong", code=500):
        super().__init__(message)
        self.message = message
        self.code = code

    def to_json(self):
        return {
            "message": self.message
        }


class NotFoundException(ServerException):
    def __init__(self, message="Not found", code=400):
        super().__init__(message, code)
