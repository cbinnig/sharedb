"""Filters a date to be only the year."""
from .filter import Filter

from dateutil.parser import parse
import datetime

class DateFilter(Filter):
    def __init__(self):
        self.year = datetime.datetime.now().year
        self.cutoff = '< ' + str(self.year - 89)

    def filter(self, column):
        for i in range(len(column)):
            try:
                date = parse(column[i])
                year = date.year
                if self.year - year > 89:
                    column[i] = self.cutoff
                else:
                    column[i] = str(year)
            except ValueError:
                column[i] = ""
        return column
