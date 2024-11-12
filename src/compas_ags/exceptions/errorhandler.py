class SolutionError(Exception):
    """Used to throw solution errors during form or force computations."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
