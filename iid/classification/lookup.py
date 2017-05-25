"""
A simple classifier that performs an in-memory lookup.
"""
from .classifier import Classifier

class Lookup(Classifier):
    """An in-memory table lookup classifier."""
    def __init__(self, data, split_input=True):
        """
        Creates a new classifier from the given data, either a list, set, dict, etc.
        Optionally splits input on classification and weights each line split on its words.

        Args:
            data (Union[set, dict, List]): The data to use for each lookup. Ensure that all
                                           data is lowercase.
            split_input (bool, optional): A flag to split the input when classifying.
        """
        self.data = data
        self.split_input = split_input

    def rate(self, column):
        score = 0
        for row in column:
            if self.split_input:
                score += sum(int(w.lower() in self.data) for w in row.split()) > 0
            else:
                score += int(row.lower() in self.data) > 0
        return score / len(column)

# TODO: Bloom filter lookup
