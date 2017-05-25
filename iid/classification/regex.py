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
SSNClassifier = Regex(None, r'\d{3}-\d{2}-\d{4}')
# Phone numbers
PhoneNumberClassifier = Regex(None, r'(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}')
# Email
EmailClassifier = Regex(None, r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
# Mac address
MACAddressClassifier = Regex(None, r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})')
# IP addresses
IPAddressClassifier = Regex(None, r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
    r'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b')
# URLs
URLClassifier = Regex(None, r'@^(https?|ftp)://[^\s/$.?#].[^\s]*$@iS')
# ZIP Code
ZipCodeClassifier = Regex(None, r'\d{5}')
# Generic number
NumberClassifier = Regex(None, r'\d')
