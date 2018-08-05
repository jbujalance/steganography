class AutoIncrementInt:

    def __init__(self, initial_value):
        self.value = initial_value

    def get_and_increment(self):
        result = self.value
        self.value += 1
        return result

    def get(self):
        return self.value
