"""
A generic class for a PII classifier.
"""
import abc

class Classifier(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def rate(self, column):
        """
        Rates a column as being PII or not.

        Args:
            columns (List[Union]): A list representing a column from a table.
        Returns:
            int: A confidence score [0.0, 1.0] as to whether this column is the given
                 type of PII.
        """

def analyze_table(table, classifiers):
    """
    Analyzes a table using the passed in classifiers.
    Returns a mapping from classifier names to their rating for each column.

    Args:
        table (Dict[str => List[Union]]): A mapping from column names to columns in a table.
        classifiers: (Dict[str => Classifier]): A mapping of classifier names to classifiers.
    Return:
        Dict[str => Dict[str => float]]: A mapping from classifier name to classifications.
    """
    classifications = {}
    for name, classifier in classifiers.items():
        ratings = {}
        for header, row in table.items():
            ratings[header] = classifier.rate(row)
        classifications[name] = ratings
    return classifications
