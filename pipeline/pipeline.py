"""
A basic pipeline structure routing from classifiers to filters.
"""
import csv
import io

from filter import Drop

class Pipe:
    """
    A class that manages both a classifier and a filter for said classifier.
    """
    def __init__(self, classifier, filter):
        """
        Creates a new Pipe with a classifier and a filter.
        The given classifier may be None to make a purely-filtering pipe.

        Args:
            classifier (Classifier): A classifier that rates 
            filter (Filter): A filter to filter a column recognized by the classifier.
        """
        self.classifier = classifier
        self.filt = filter

    def rate(self, column):
        """Rates the column using this Pipe's classifier."""
        if self.classifier is None:
            return 0
        return self.classifier.rate(column)

    def filter(self, column):
        """Filters the column using this Pipe's filter."""
        return self.filt.filter(column)

DROP_PIPE = Pipe(None, Drop())

def rotate_table(table):
    """Transforms a list of dictionaries into a dictionaries of lists."""
    names = table[0].keys()
    columns = {}
    for name in names:
        columns[name] = []
    for row in table:
        for name in names:
            columns[name].append(row[name])
    return columns

class Pipeline:
    """
    A class that manages a set of Pipes that control the classification
    to filtering flow.
    """
    def __init__(self):
        """
        Creates a new, empty Pipeline. Registers the simple drop Pipe
        in order to ensure that we can always drop data.
        """
        self.data = None
        self.columns = []
        self.ratings = {}
        self.pipes = {}
        self.add_pipe('DROP', DROP_PIPE)

    def add_data(self, dataset):
        """
        Sets up the Pipeline to work with the given dataset.

        Args:
            dataset: The dataset to work with, either a list of dictionaries
                     or a dictionary of lists.
        """
        if isinstance(dataset, list):
            self.data = rotate_table(dataset)
        else:
            self.data = dataset
        self.columns = list(self.data.keys())

    def add_pipe(self, id, pipe):
        """
        Adds a new Pipe to the Pipeline.

        Args:
            id (str): A unique identifier for the Pipe.
            Pipe (Pipe): Pipe.
        """
        if id in self.pipes:
            raise RuntimeError("ID already exists in pipeline.")
        self.pipes[id] = pipe

    def classify(self):
        """
        Classifies this pipeline's data.

        Returns:
            Dict[str => Dict[str => float]]: A dictionary of classification scores.
        """
        ratings = {}
        for header, column in self.data.items():
            scores = {}
            for name, pipe in self.pipes.items():
                if pipe.classifier is None:
                    continue
                scores[name] = pipe.rate(column)
            ratings[header] = scores
        self.ratings = ratings
        return ratings

    def filter(self, choices):
        """
        Filters the data using the given filtering choices.

        Args:
            choices (Dict[str => str]): A mapping from column names to Pipe IDs.
        """
        for column, id in choices.items():
            self.data[column] = self.pipes[id].filter(self.data[column])

    def csv(self):
        """
        Returns this Pipeline's data as a CSV.
        """
        with io.StringIO() as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
            for i in range(len(self.data[self.columns[0]])):
                row = {column: self.data[column][i] for column in self.columns}
                writer.writerow(row)
            return f.getvalue()
