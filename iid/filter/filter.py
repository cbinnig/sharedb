"""
A base class for Filter objects which modify columns in a database
to remove PII or similar.
"""
import abc

class Filter(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def filter(self, column):
        """
        Filters the given column in place.

        Args:
            column (List[Union]): A list of elements representing a column in a database.
        Returns:
            List[Union]: The filtered column.
        """

class Drop(Filter):
    def __init__(self):
        pass

    """
    A special filter that drops a column.
    """
    def filter(self, column):
        for i in range(len(column)):
            column[i] = None
        return column
