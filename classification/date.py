"""Classifies dates."""
from .classifier import Classifier

from dateutil.parser import parse

class DateClassifier(Classifier):
    def __init__(self):
        pass

    def rate(self, column):
        score = 0
        for row in column:
            try:
                parse(row)
                score += 1
            except ValueError:
                pass
        return score / len(column)
