# Infer schema

Infer JSON schema from CSV files.

## Installation

The script can be installed via pip

```shell
pip install infer-schema
```

Currently, infer-schema is a single Python 3 script without any external
dependencies, so you can download it to somewhere in your PATH and make it
executable:

```shell
curl https://raw.githubusercontent.com/abhidg/infer-schema/main/infer_schema.py -o infer-schema
chmod +x infer-schema
./infer-schema file
```

## Usage

See [infer-schema(1)](infer-schema.1.scd)
(from a local clone, use `man ./infer-schema.1`)

For the Python library interface, see below.

## Examples

With a data file like

```csv
date,count
2023-11-20,10
2023-11-21,23
```

Running infer-schema will produce a JSON Schema that the CSV conforms to:

```json
{
  "$schema": "https://json-schema.org/draft-07/schema",
  "description": "Description of data.csv",
  "properties": {
    "count": {
      "description": "Description for column count",
      "maximum": 23,
      "minimum": 10,
      "type": "integer"
    },
    "date": {
      "description": "Description for column date",
      "format": "date",
      "type": "string"
    }
  },
  "required": [
    "date",
    "count"
  ],
  "title": "JSON Schema for data.csv"
}
```

## Python library

The same result can be obtained using the Python module:

```python
from infer_schema import infer_schema

schema = infer_schema("data.csv")
print(schema)
```

### Parameters

**infer_schema**(file: Union[*Path*, *str*],
    enum_threshold: *int* = 10,
    enum_fields: List[*str*] = [],
    bound_types: Set[*DType*] = {"integer", "number"},
    explicit_nulls: *bool* = False)

Here *DType* is one of *number*, *integer* or *string*.

* **file** (*Path* or *str*): CSV file

* **enum_threshold** (*int*, default = 10): Threshold of number of
   unique values in column below which the field is typed enum

* **enum_fields** (List[*str*], default = []): Forces a certain field to be
   classed as an enum, useful for including fields that do not meet
   `enum-threshold` criteria

* **bound_types** (Set[*DType*], default = `{"integer", "number"}`): Types for
  which bounds should be encoded into the schema, default is numbers, for which
  minimum / maximum are determined. For strings minLength and maxLength are
  determined. Set to `None` to disable bound detection

* **explicit_nulls** (*bool*, default = False): By default, fields that have
  null and another type are typed as non-required with the non-null type.
  Another interpretation is to assume the field will be present and allow it to
  dual-typed with null.

**Returns**: JSON Schema as a dictionary

## Development

Install pre-commit to setup ruff linting and formatting.

To generate the man page, [scdoc](https://git.sr.ht/~sircmpwn/scdoc) is required:

```shell
scdoc < infer-schema.1.scd > infer-schema.1
```
