class SteganographyException(Exception):
    pass


class CapacityException(SteganographyException):
    def __init__(self, content_size, available_size):
        self.content_size = content_size
        self.available_size = available_size
        self.message = "The size of the content (" + content_size / 1000 + " Kb) is greater than the available size (" + available_size / 1000 + " Kb)"


class NoMessageFoundException(SteganographyException):
    def __init__(self, message):
        self.message = message
