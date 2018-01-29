# -*- coding: utf-8 -*-

import json
import jsonschema
import pprint
import jsonselect
import objectpath
from jsonpath_rw_ext import parse
from jsonpath_rw.parser import DatumInContext, Index, Fields


class JsonValidator(object):
    """
    Library for JSON validating.
    Based on: JSONSchema, JSONPath, JSONSelect.

    == Additional Information ==
    - [ http://json-schema.org/ | Json Schema ]
    - [ http://www.jsonschema.net/ | Jsonschema generator ]
    - [ http://goessner.net/articles/JsonPath/ | JSONPath by Stefan Goessner ]
    - [ http://jsonpath.curiousconcept.com/ | JSONPath Tester ]
    - [ http://jsonselect.org/ | JSONSelect]
    - [ http://jsonselect.curiousconcept.com/ | JSONSelect Tester]

    == Dependencies ==
    | jsonschema | https://pypi.python.org/pypi/jsonschema |
    | jsonpath-rw-ext | https://pypi.python.org/pypi/jsonpath-rw-ext |
    | objectpath | https://pypi.python.org/pypi/objectpath/ |
    | pyjsonselect | https://pypi.python.org/pypi/pyjsonselect |

    == Example of use ==
    json_example.json
    | { "store": {
    |        "book": [
    |          { "category": "reference",
    |            "author": "Nigel Rees",
    |            "title": "Sayings of the Century",
    |            "price": 8.95
    |          },
    |          { "category": "fiction",
    |            "author": "Evelyn Waugh",
    |            "title": "Sword of Honour",
    |            "price": 12.99
    |          },
    |          { "category": "fiction",
    |            "author": "Herman Melville",
    |            "title": "Moby Dick",
    |            "isbn": "0-553-21311-3",
    |            "price": 8.99
    |          },
    |          { "category": "fiction",
    |            "author": "J. R. R. Tolkien",
    |            "title": "The Lord of the Rings",
    |            "isbn": "0-395-19395-8",
    |            "price": 22.99
    |          }
    |        ],
    |        "bicycle": {
    |          "color": "red",
    |          "price": 19.95
    |        }
    |  }
    | }

    | *Settings* | *Value* |
    | Library    | JsonValidator |
    | Library    | OperatingSystem |
    | *Test Cases* | *Action* | *Argument* | *Argument* |
    | Check element | ${json_example}=   | OperatingSystem.Get File |   ${CURDIR}${/}json_example.json |
    | | Element should exist  |  ${json_example}  |  .author:contains("Evelyn Waugh") |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def _validate_json(self, checked_json, schema):
        """ Validating JSON according to JSONSchema

        *Args*:\n
        _checked_json_: validated JSON.
        _schema_: schema that used for validating.
        """
        try:
            jsonschema.validate(checked_json, schema)
        except jsonschema.ValidationError as e:
            print("""Failed validating '{0}'
in schema {1}:
{2}
On instance {3}:
{4}""".format(e.validator,
              list(e.relative_schema_path)[:-1],
              pprint.pformat(e.schema),
              "[%s]" % "][".join(repr(index) for index in e.absolute_path),
              pprint.pformat(e.instance).encode('utf-8')))
            raise JsonValidatorError("Failed validating json by schema")
        except jsonschema.SchemaError as e:
            raise JsonValidatorError('Json-schema error')

    def validate_jsonschema_from_file(self, json_string, path_to_schema):
        """
        Validating JSON according to schema, loaded from a file.

        *Args:*\n
        _json_string_ - JSON string;\n
        _path_to_schema_ - path to file with JSON schema;

        *Raises:*\n
        JsonValidatorError

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | Simple | Validate jsonschema from file  |  {"foo":bar}  |  ${CURDIR}${/}schema.json |
        """
        schema = open(path_to_schema).read()
        load_input_json = self.string_to_json(json_string)

        try:
            load_schema = json.loads(schema)
        except ValueError as e:
            raise JsonValidatorError('Error in schema: {}'.format(e))

        self._validate_json(load_input_json, load_schema)

    def validate_jsonschema(self, json_string, input_schema):
        """
        Validating JSON according to schema.

        *Args:*\n
        _json_string_ - JSON string;\n
        _input_schema_ - schema in string format;

        *Raises:*\n
        JsonValidatorError

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | Library    | OperatingSystem |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | Simple | ${schema}=   | OperatingSystem.Get File |   ${CURDIR}${/}schema_valid.json |
        |  | Validate jsonschema  |  {"foo":bar}  |  ${schema} |
        """
        load_input_json = self.string_to_json(json_string)

        try:
            load_schema = json.loads(input_schema)
        except ValueError as e:
            raise JsonValidatorError('Error in schema: {}'.format(e))

        self._validate_json(load_input_json, load_schema)

    def string_to_json(self, source):
        """
        Deserialize string into JSON structure.

        *Args:*\n
        _source_ - JSON string

        *Returns:*\n
        JSON structure

        *Raises:*\n
        JsonValidatorError

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | Library    | OperatingSystem |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | String to json  | ${json_string}=   | OperatingSystem.Get File |   ${CURDIR}${/}json_example.json |
        |                 |  ${json}= | String to json  |  ${json_string} |
        |                 |  Log | ${json["store"]["book"][0]["price"]} |
        =>\n
        8.95
        """
        try:
            load_input_json = json.loads(source)
        except ValueError as e:
            raise JsonValidatorError("Could not parse '%s' as JSON: %s" % (source, e))
        return load_input_json

    def json_to_string(self, source):
        """
        Serialize JSON structure into string.

        *Args:*\n
        _source_ - JSON structure

        *Returns:*\n
        JSON string

        *Raises:*\n
        JsonValidatorError

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | Library    | OperatingSystem |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | Json to string  | ${json_string}=   | OperatingSystem.Get File |   ${CURDIR}${/}json_example.json |
        |                 | ${json}= | String to json |   ${json_string} |
        |                 | ${string}=  |  Json to string  |  ${json} |
        |                 | ${pretty_string}=  |  Pretty print json  |  ${string} |
        |                 | Log to console  |  ${pretty_string} |
        """
        try:
            load_input_json = json.dumps(source)
        except ValueError as e:
            raise JsonValidatorError("Could serialize '%s' to JSON: %s" % (source, e))
        return load_input_json

    def get_elements(self, json_string, expr):
        """
        Get list of elements from _json_string_, matching [http://goessner.net/articles/JsonPath/|JSONPath] expression.

        *Args:*\n
        _json_string_ - JSON string;\n
        _expr_ - JSONPath expression;

        *Returns:*\n
        List of found elements or ``None`` if no elements were found

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | Library    | OperatingSystem |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | Get json elements | ${json_example}=   | OperatingSystem.Get File |   ${CURDIR}${/}json_example.json |
        |                   |  ${json_elements}= | Get elements  |  ${json_example}  |  $.store.book[*].author |
        =>\n
        | [u'Nigel Rees', u'Evelyn Waugh', u'Herman Melville', u'J. R. R. Tolkien']
        """
        load_input_json = self.string_to_json(json_string)
        # parsing jsonpath
        jsonpath_expr = parse(expr)
        # list of returned elements
        value_list = []
        for match in jsonpath_expr.find(load_input_json):
            value_list.append(match.value)
        if not value_list:
            return None
        else:
            return value_list

    def select_elements(self, json_string, expr):
        """
        Return list of elements from _json_string_, matching [ http://jsonselect.org/ | JSONSelect] expression.

        *DEPRECATED* Язык запросов JSON Select query language is outdated and not supported any more.
        Use other keywords of this library to query JSON.

        *Args:*\n
        _json_string_ - JSON string;\n
        _expr_ - JSONSelect expression;

        *Returns:*\n
        List of found elements or ``None`` if no elements were found

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | Library    | OperatingSystem |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | Select json elements | ${json_example}=   | OperatingSystem.Get File |   ${CURDIR}${/}json_example.json |
        |                      |  ${json_elements}= | Select elements  |  ${json_example}  |  .author:contains("Evelyn Waugh")~.price |
        =>\n
        | 12.99
        """
        load_input_json = self.string_to_json(json_string)
        # parsing jsonselect
        match = jsonselect.match(sel=expr, obj=load_input_json)
        ret = list(match)
        return ret if ret else None

    def select_objects(self, json_string, expr):
        """
        Return list of elements from _json_string_, matching [ http://objectpath.org// | ObjectPath] expression.

        *Args:*\n
        _json_string_ - JSON string;\n
        _expr_ - ObjectPath expression;

        *Returns:*\n
        List of found elements. If no elements were found, empty list will be returned

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | Library    | OperatingSystem |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | Select json objects  | ${json_example}=   | OperatingSystem.Get File |   ${CURDIR}${/}json_example.json |
        |                      |  ${json_objectss}= | Select objects  |  ${json_example}  |  $..book[@.author.name is "Evelyn Waugh"].price |
        =>\n
        | [12.99]
        """
        load_input_json = self.string_to_json(json_string)
        # parsing objectpath
        tree = objectpath.Tree(load_input_json)
        values = tree.execute(expr)
        return list(values)

    def element_should_exist(self, json_string, expr):
        """
        Check the existence of one or more elements, matching [ http://jsonselect.org/ | JSONSelect] expression.

        *DEPRECATED* Язык запросов JSON Select query language is outdated and not supported any more.
        Use other keywords of this library to query JSON.

        *Args:*\n
        _json_string_ - JSON string;\n
        _expr_ - JSONSelect expression;\n

        *Raises:*\n
        JsonValidatorError

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | Library    | OperatingSystem |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | Check element | ${json_example}=   | OperatingSystem.Get File |   ${CURDIR}${/}json_example.json |
        | | Element should exist  |  ${json_example}  |  .author:contains("Evelyn Waugh") |
        | | Element should exist  |  ${json_example}  |  .store .book  .price:expr(x=8.95) |
        """
        value = self.select_elements(json_string, expr)
        if value is None:
            raise JsonValidatorError('Elements %s does not exist' % expr)

    def element_should_not_exist(self, json_string, expr):
        """
        Check that one or more elements, matching [ http://jsonselect.org/ | JSONSelect] expression, don't exist.

        *DEPRECATED* Язык запросов JSON Select query language is outdated and not supported any more.
        Use other keywords of this library to query JSON.

        *Args:*\n
        _json_string_ - JSON string;\n
        _expr_ - JSONSelect expression;\n

        *Raises:*\n
        JsonValidatorError
        """
        value = self.select_elements(json_string, expr)
        if value is not None:
            raise JsonValidatorError('Elements %s exist but should not' % expr)

    def _json_path_search(self, json_dict, expr):
        """
        Scan JSON dictionary with using json-path passed sting of the format of $.element..element1[index] etc.

        *Args:*\n
        _json_dict_ - JSON dictionary;\n
        _expr_ - string of fuzzy search for items within the directory;\n

        *Returns:*\n
        List of DatumInContext objects:
        ``[DatumInContext(value=..., path=..., context=[DatumInContext])]``
        - value - found value
        - path  - value selector inside context.value (in implementation of jsonpath-rw: class Index or Fields)

        *Raises:*\n
        JsonValidatorError
        """
        path = parse(expr)
        results = path.find(json_dict)

        if len(results) is 0:
            raise JsonValidatorError("Nothing found in the dictionary {0} using the given path {1}".format(str(json_dict), str(expr)))

        return results

    def update_json(self, json_string, expr, value, index=0):
        """
        Replace the value in the JSON string.

        *Args:*\n
        _json_string_ - JSON string;\n
        _expr_ - JSONPath expression for determining the value to be replaced;\n
        _value_ - the value to be replaced with;\n
        _index_ - index for selecting item within a match list, default value is 0;\n

        *Returns:*\n
        Changed JSON in dictionary format.

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | Library    | OperatingSystem |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | Update element | ${json_example}=   | OperatingSystem.Get File |   ${CURDIR}${/}json_example.json |
        | | ${json_update}= | Update_json  |  ${json_example}  |  $..color  |  changed |
        """
        load_input_json = self.string_to_json(json_string)
        matches = self._json_path_search(load_input_json, expr)

        datum_object = matches[int(index)]

        if not isinstance(datum_object, DatumInContext):
            raise JsonValidatorError("Nothing found by the given json-path")

        path = datum_object.path

        # Edit the directory using the received data
        # If the user specified a list
        if isinstance(path, Index):
            datum_object.context.value[datum_object.path.index] = value
        # If the user specified a value of type (string, bool, integer or complex)
        elif isinstance(path, Fields):
            datum_object.context.value[datum_object.path.fields[0]] = value

        return load_input_json

    def pretty_print_json(self, json_string):
        """
        Return formatted JSON string _json_string_.\n
        Method json.dumps with _indent=2, ensure_ascii=False_ setting is used.

        *Args:*\n
        _json_string_ - JSON string.

        *Returns:*\n
        Formatted JSON string.

        *Example:*\n
        | *Settings* | *Value* |
        | Library    | JsonValidator |
        | Library    | OperatingSystem |
        | *Test Cases* | *Action* | *Argument* | *Argument* |
        | Check element | ${pretty_json}=   | Pretty print json |   {a:1,foo:[{b:2,c:3},{d:"baz",e:4}]} |
        | | Log  |  ${pretty_json}  |
        =>\n
        | {
        |    "a": 1,
        |    "foo": [
        |      {
        |        "c": 3,
        |        "b": 2
        |      },
        |      {
        |        "e": 4,
        |        "d": "baz"
        |      }
        |    ]
        | }
        """
        return json.dumps(self.string_to_json(json_string), indent=2, ensure_ascii=False)


class JsonValidatorError(Exception):
    pass
