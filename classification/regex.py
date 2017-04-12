"""
A simple SSN classifier based on using a regex.
"""
import re

from .classifier import Classifier

class Regex(Classifier):
    def __init__(self, preprocess, *args):
        """
        Creates a classifier based on the provided raw string regex.
        Args:
            preprocess [(str) => str]: A function that transforms a string to a string.
            *args (str): A list of raw strings to be used as regex.
        """
        if preprocess is not None:
            self.preprocess = preprocess
        else:
            self.preprocess = lambda x: x
        self.regex = []
        for s in args:
            self.regex.append(re.compile(s))

    def rate(self, column):
        matches = 0
        for row in column:
            if any(regex.match(self.preprocess(row)) is not None for regex in self.regex):
                matches += 1
        return matches / len(column)

# Common PII regex
# Social security numbers
SSN = Regex(None, r'\d{3}-\d{2}-\d{4}')
# Phone numbers
PhoneNumber = Regex(None, r'(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}')
# Email
Email = Regex(None, r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}')
# Mac address
MAC = Regex(None, r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})')
# ZIP Code
ZIPCODE = Regex(None, r'\d{5}')