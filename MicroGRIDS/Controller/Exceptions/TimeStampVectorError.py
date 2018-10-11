# Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: Feb 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Contains custom error class to be raised if there are issues with time stamps detected.


class TimeStampVectorError(Exception):
    """
    Exception raised for issues with the time stamp vector used in other optimizer routines.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message