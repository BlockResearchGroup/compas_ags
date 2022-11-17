from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__all__ = ["SolutionError"]


class SolutionError(Exception):
    """Used to throw solution errors during form or force computations."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
