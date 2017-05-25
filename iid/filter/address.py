"""Address filter"""
from .filter import Filter
from .zip_code import ZipCodeFilter

import usaddress

class AddressFilter(Filter):
    def __init__(self):
        self.zip_filter = ZipCodeFilter()

    def filter(self, column):
        """
        Removes addresses and pares them down to their filtered zip codes.
        """
        for i in range(len(column)):
            row = column[i]
            try:
                tagged = usaddress.tag(row)
                if len(tagged) < 1:
                    column[i] = '000'
                else:
                    addr = tagged[0]
                    column[i] = addr['ZipCode']
            except:
                column[i] = '000'
        return self.zip_filter.filter(column)
