"""This module contains a class, Configuration, that holds the configuration parameters of the running program."""

# Python import.
import json

# User imports.
from . import generate_dict_paths
from . import json_schema_operations

# 3rd party imports.
import jsonschema


class Configuration(object):

    def __init__(self, **kwargs):
        """Initialise a Configuration object.

        :param kwargs:  Keyword arguments to initialise.
        :type kwargs:   dict

        """

        self._configParams = {}
        self.set_from_dict(kwargs)

    def get_param(self, path):
        """Extract a configuration parameter from the dictionary of parameters.

        :param path:    The path through the configuration parameter dictionary to use to extract the parameter.
        :type path:     list[str]
        :return:        The parameter's value or an indication that the parameter does not exist.
        :rtype:         bool, list | int | str | float | dict | None
                            1st element indicates whether the parameter was found.
                            2nd element is the parameter's value if found and the name of the first missing dictionary
                                key if not found (e.g. "A" if self._configParams["B"]["A"]["C"] fails because "A"
                                is not a key in the self._configParams["B"] dictionary.

        """

        paramFound = False  # Whether the parameter was found.
        paramValue = self._configParams  # The value to return.
        for i in path:
            if i in paramValue:
                # The next element in the path was found, so keep looking.
                paramValue = paramValue[i]
            else:
                # The parameter was not found, so terminate the search.
                paramValue = i
                break
        else:
            # The parameter was found as all elements in the path were found.
            paramFound = True

        return paramFound, paramValue

    def set_from_dict(self, paramsToAdd):
        """Set configuration parameters from a dictionary of parameters.

        This will overwrite any existing parameters with the same name.

        :param paramsToAdd:  Parameters to add.
        :type paramsToAdd:   dict

        """

        self._configParams.update(paramsToAdd)

    def set_from_json(self, config, schema, newEncoding=None, storeDefaults=True):
        """Add parameters to a Configuration object from a JSON formatted file or dict.

        Any configuration parameters that the user has defined will overwrite existing parameters with the same name.
        Storing defaults will never overwrite user-defined or pre-existing parameters.

        :param config:          The location of a JSON file or a loaded JSON object containing the configuration
                                information to add.
        :type config:           str | dict
        :param schema:          The schema that the configuration information must be validated against. This can either
                                be a file location or a loaded JSON object.
        :type schema:           str | dict
        :param newEncoding:     The encoding to convert all strings in the JSON configuration object to.
        :type newEncoding:      str
        :param storeDefaults:   Whether defaults from the schema should be stored. Defaults will never overwrite
                                    existing or user-defined parameters.
        :type storeDefaults:    bool

        """

        # Extract the JSON data.
        if isinstance(config, str):
            fid = open(config, 'r')
            config = json.load(fid)
            if newEncoding:
                config = json_schema_operations.change_encoding(config, newEncoding)
            fid.close()

        # Extract the schema information.
        if isinstance(schema, str):
            fid = open(schema, 'r')
            schema = json.load(fid)
            if newEncoding:
                schema = json_schema_operations.change_encoding(schema, newEncoding)
            fid.close()

        # Validate the configuration data.
        jsonschema.validate(config, schema)

        # Set schema defaults.
        if storeDefaults:
            extractedDefaults, defaultsExtracted = json_schema_operations.extract_schema_defaults(schema)
            for i in generate_dict_paths.main(extractedDefaults):
                self.set_param(*i, overwrite=False)

        # Add the configuration parameters.
        for i in generate_dict_paths.main(config):
                self.set_param(*i, overwrite=True)

    def set_param(self, path, value, overwrite=False):
        """Set a configuration parameter by path.

        :param path:        The path through the configuration parameter dictionary to use to set the parameter.
        :type path:         list[str]
        :param value:       The parameter value to insert.
        :type value:        object
        :param overwrite:   Whether an existing parameter at the path should be overwritten.
        :type overwrite:    bool

        """

        paramExists = self.get_param(path)[0]  # Whether a parameter already exists at the path specified.

        if (not paramExists) or overwrite:
            # We need to add the parameter or overwrite the existing value of it.
            pass

            paramValue = self._configParams  # The value to return.
            for i in path[:-1]:
                if i not in paramValue:
                    # The nest element in the path could not be found, so add it to the parameter dictionary.
                    paramValue[i] = {}
                paramValue = paramValue[i]

            paramValue[path[-1]] = value
