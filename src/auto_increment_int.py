class AutoIncrementInt:
    """
    A pretty ugly class meant to replace the behaviour of the classic 'int++' which does not exist in Python
    """

    def __init__(self, initial_value):
        self.value = initial_value

    def get_and_increment(self):
        current = self.value
        self.value += 1
        return current

    def get(self):
        return self.value
