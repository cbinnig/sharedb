"""Zip code filter"""
from .filter import Filter

# From 2000 census data, these are the 17 exceptions to ZIP code
# de-identification and must be changed to 000 as there are less than 20k
# people in these areas.
exceptions = ['036',
              '692',
              '878',
              '059',
              '790',
              '879',
              '063',
              '821',
              '884',
              '102',
              '823',
              '890',
              '203',
              '830',
              '893',
              '556',
              '831']

class ZipCodeFilter(Filter):
    def __init__(self):
        pass

    def filter(self, column):
        for i in range(len(column)):
            code = str(column[i])
            if len(code) > 5 and '-' not in code:
                code = '000'
            else:
                code = code[:3]
                if code in exceptions:
                    code = '000'
            column[i] = code
        return column
