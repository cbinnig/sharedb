"""
A classifier for addresses that relies on the pyap library.
"""
from .classifier import Classifier

import usaddress

class AddressClassifier(Classifier):
    """
    An address classifier that can detect arbitrary addresses
    in text.
    """
    def __init__(self):
        pass

    def rate(self, column):
        score = 0
        for row in column:
            try:
                tagged = usaddress.tag(row)
                score += len(tagged) > 0 and 'ZipCode' in tagged[0]
            except:
                pass
        return score / len(column)
