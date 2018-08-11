class SteganographyException(Exception):
    pass


class CapacityException(SteganographyException):
    def __init__(self, content_size, available_size):
        self.content_size = content_size
        self.available_size = available_size


class NoMessageFoundException(SteganographyException):
    def __init__(self, message):
        self.message = message
