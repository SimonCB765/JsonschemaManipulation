"""Function to generate paths through a nested dictionary for each value in the dictionary."""

# Python imports.
import operator
import sys

# Define functions for compatibility.
if sys.version_info[0] >= 3:
    iteritems = operator.methodcaller("items")
else:
    iteritems = operator.methodcaller("iteritems")


def main(nestedDict, path=None):
    """Extract the paths through dictionary keys needed to reach each value.

    :param nestedDict:  The (sub-)dictionary to search through.
    :type nestedDict:   dict
    :param path:        The path to the current point in the dictionary.
    :type path:         list
    :return:            The value and the path through the keys that reaches it.
    :rtype:             list, object

    """

    if path is None:
        path = []
    for key, value in iteritems(nestedDict):
        newpath = path + [key]
        if isinstance(value, dict):
            # If the current value is a dictionary, then we dive further into the nested dictionary.
            for i in main(value, newpath):
                yield i
        else:
            # If the current value is not a dictionary, then we return the value and the path taken to reach it.
            yield newpath, value
