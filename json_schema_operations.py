"""Code for manipulating JSON schemas."""

# Python imports.
import operator
import sys

# Define functions for compatibility.
if sys.version_info[0] >= 3:
    from functools import reduce
    basestring = unicode = str
    iteritems = operator.methodcaller("items")
else:
    iteritems = operator.methodcaller("iteritems")


def change_encoding(jsonObject, encoding="utf-8"):
    """Convert unicode strings in a JSON object to a given encoding.

    The primary purpose of this is to convert unicode strings generated in Python 2 to ascii (utf-8)

    This will recurse through all levels of the JSON dictionary, and therefore may hit Python's recursion limit.
    To avoid this use object_hook in the json.load() function instead.

    :param jsonObject:  The JSON object.
    :type jsonObject:   dict
    :param encoding:    The encoding to use.
    :type encoding:     str
    :return:            The JSON object with all strings encoded as desired.
    :rtype:             dict

    """

    if isinstance(jsonObject, dict):
        # If the current part of the JSON object is a dictionary, then encode all its keys and values if needed.
        return dict(
            [(change_encoding(key, encoding), change_encoding(value, encoding)) for key, value in iteritems(jsonObject)]
        )
    elif isinstance(jsonObject, list):
        # If the current part of the JSON object is a list, then encode all its elements if needed.
        return [change_encoding(i, encoding) for i in jsonObject]
    elif isinstance(jsonObject, basestring):
        # If you've reached a string then encode.
        return jsonObject.encode(encoding)
    else:
        # You've reached a non-unicode terminus (e.g. an integer or null).
        return jsonObject


def extract_schema_defaults(schema):
    """Extract the default attribute values derived from the types and defaults specified in a JSON schema.

    If no user supplied default is present in the schema for a given element, then only a "null" element will get a
    default defined for it (a default of None). Only elements with defaults set (either on themselves or a sub-schema)
    will have defaults returned.

    Points to note are:
        - Validation of the schema structure is not performed. The schema should therefore be validated first.
        - Validation of the default values is not performed. It is up to the schema writer to ensure they are legal.
        - References are all treated as references to top level elements of the schema outside the "properties" element.
            Traditionally the referenced elements would be held in a top level "definitions" object.
        - Defaults specified in a sub-schema will override those specified higher up the schema hierarchy. For example,
            {
                "default": {"key": 0},
                "type": "object",
                "key": {"default": 1, "type": "integer"}
            }
            will produce a default of {"key": 1} not {"key": 0}.
        - There is no need to set a default for a required element of a (sub-)schema (although there is no requirement
            not to) as a value has to be supplied in each instantiation of the schema for the instantiation to
            validate successfully.

    :param schema:  A JSON object containing a schema that the instantiations will be evaluated against.
    :type schema:   dict
    :return:        The default values for the current (sub-)schema.
    :rtype:         dict

    """

    # The returned results for this (sub-)schema. Two variables are needed as every Falsey value is a possible valid
    # default value that can be returned. It's therefore not possible to simple test the returned defaults value for
    # truthiness in order to determine whether default values were found. Nor is it possible to test for None
    # explicitly as the default value for a "null" type element is None, so this is also a valid default value.
    schemaDefaults = {}
    defaultsFound = False

    # Go through each element in the (sub-)schema and determine if it has a default value.
    for i, j in iteritems(schema.get("properties")):
        # If the element value is a reference, then replace the reference with the referenced element.
        if "$ref" in j.keys():
            defPath = j.get("$ref").split("/")[1:]  # Ignore the '#' at the beginning of the ref path.
            j = reduce(lambda d, key: d.get(key) if d else None, defPath, schema)

        # Determine the type of the element.
        elementType = j.get("type")

        if elementType == "object":
            # The element is an object, so try and extract its defaults.
            schema["properties"] = j["properties"]
            elementDefaults, defaultExtracted = extract_schema_defaults(schema)
            if defaultExtracted:
                defaultsFound = True
                schemaDefaults[i] = elementDefaults
        elif elementType in ["array", "boolean", "integer", "number", "string"]:
            # The element is a basic type, so we just need to try and extract a default value.
            default = j.get("default", None)
            if default is not None:
                schemaDefaults[i] = default
                defaultsFound = True
        elif elementType == "null":
            # The element is a null type, so just leave the default as None.
            defaultsFound = True
            schemaDefaults[i] = None

    return schemaDefaults, defaultsFound
