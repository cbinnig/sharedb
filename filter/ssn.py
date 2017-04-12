"""SSN Filter"""
from .filter import Filter

class SSNFilter(Filter):
    def __init__(self):
        pass

    def filter(self, column):
        for i in range(len(column)):
            ssn = str(column[i])
            ssn = ssn[-4:]
            column[i] = ssn
        return column