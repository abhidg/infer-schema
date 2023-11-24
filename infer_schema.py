#!/usr/bin/env python3
import csv
import json
import argparse
from datetime import datetime
from collections import defaultdict
from contextlib import suppress
from typing import Union, List, Dict, Any, Literal, Set, Optional, Sequence
from pathlib import Path

DType = Literal[
    "number", "integer", "string", "string:date", "string:date-time", "null"
]
NULL_VALUES = {"N/A", "N/K", "NA", "NK", ""}
DEFAULT_ENUM_THRESHOLD = 10


def _detect_type(val: str) -> DType:
    if val in NULL_VALUES:
        return "null"
    if val.isdigit():
        return "integer"
    with suppress(ValueError):
        float(val)
        return "number"
    with suppress(ValueError):
        datetime.strptime(val, "%Y-%m-%d")
        return "string:date"
    with suppress(ValueError):
        datetime.strptime(val, "%Y-%m-%dT%H:%M:%S%z")
        return "string:date-time"
    return "string"


def _json_schema_types(typeset: Set[str]) -> List[str]:
    formats = set(x.partition(":")[-1] for x in typeset) - {""}
    types = set(x.partition(":")[0] for x in typeset)
    if types == {"string"} and len(formats) == 1:
        return {
            "type": "string",
            "format": list(formats)[0],
        }
    elif len(types) == 1:
        return {"type": list(types)[0]}
    else:
        return {"type": sorted(types)}


def infer_schema(
    file: Union[Path, str],
    enum_threshold: int = DEFAULT_ENUM_THRESHOLD,
    enum_fields: List[str] = [],
    bound_types: Set[DType] = {"integer", "number"},
    explicit_nulls: bool = False,
) -> Dict[str, Any]:
    """Infer schema from CSV file

    Parameters
    ----------
    file: CSV file

    enum_threshold: Threshold of number of unique values in column below
      which the field is typed enum

    enum_fields: Forces a certain field to be classed as an enum, useful
      for including fields that do not meet `enum-threshold` criteria

    bound_types: Types for which bounds should be encoded into the schema,
      default is numbers, for which minimum / maximum are determined. For
      strings minLength and maxLength are determined. Set `--bound-types=none`
      to disable bound detection

    explicit_nulls: By default, fields that have null and another type are typed
      as non-required with the non-null type. Another interpretation is to
      assume the field will be present and allow it to dual-typed with null.

    Returns
    -------
    JSON schema
    """
    jsonschema = {
        "$schema": "https://json-schema.org/draft-07/schema",
        "title": f"JSON Schema for {file}",
        "description": "Inferred JSON Schema from infer-schema",
    }
    unique_values: Dict[str, Set[Any]] = defaultdict(set)
    properties = {}

    # Read header
    n_records = 0
    with open(file) as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            n_records += 1
            for column in row:
                unique_values[column].add(row[column])
    has_nulls = set(c for c in unique_values if unique_values[c] & NULL_VALUES)
    if not explicit_nulls:
        unique_values = {c: unique_values[c] - NULL_VALUES for c in unique_values}
    column_types = {c: set(map(_detect_type, unique_values[c])) for c in unique_values}
    integer_columns = [
        c for c in column_types if column_types[c] == {"integer"} and unique_values[c]
    ]
    numeric_columns = [
        c
        for c in column_types
        if column_types[c] in [{"number"}, {"number", "integer"}] and unique_values[c]
    ]
    unique_numeric_values = {
        c: list(map(float, unique_values[c])) for c in numeric_columns
    }
    unique_numeric_values.update(
        {c: list(map(int, unique_values[c])) for c in integer_columns}
    )
    minimums = {c: min(unique_numeric_values[c]) for c in unique_numeric_values}
    maximums = {c: max(unique_numeric_values[c]) for c in unique_numeric_values}

    jsonschema["description"] = "Description of " + file
    jsonschema["required"] = [c for c in unique_values if c not in has_nulls]
    for c in unique_values:
        if not unique_values[c]:
            properties[c] = {"type": "null"}
        elif len(unique_values[c]) == 1:
            const_val = list(unique_values[c])[0]
            if const_val in NULL_VALUES:
                properties[c] = {"type": "null"}
            else:
                properties[c] = {"const": const_val}
        elif (
            c in enum_fields or 1 < len(unique_values[c]) <= enum_threshold < n_records
        ):
            if c in integer_columns or c in numeric_columns:
                properties[c] = {"enum": sorted(unique_numeric_values[c])}
            else:
                properties[c] = {
                    "enum": [
                        x if x not in NULL_VALUES else None
                        for x in sorted(unique_values[c])
                    ]
                }
        elif column_types[c]:
            properties[c] = _json_schema_types(column_types[c])
            if bound_types & {"integer", "number"} and (
                c in numeric_columns or c in integer_columns
            ):
                properties[c].update(dict(minimum=minimums[c], maximum=maximums[c]))

        else:  # no types detected, default to string
            properties[c] = {"type": "string"}
        if {"string"} & bound_types & column_types[c] and not (
            c in enum_fields or 0 < len(unique_values[c]) <= enum_threshold
        ):
            properties[c].update(
                dict(
                    minLength=min(map(len, unique_values[c])),
                    maxLength=max(map(len, unique_values[c])),
                )
            )
        properties[c]["description"] = f"Description for column {c}"

    jsonschema["properties"] = properties
    return jsonschema


def main(cmd_args: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(description="Infer JSON schema from CSV")
    parser.add_argument("filename", help="Filename to infer schema for")
    parser.add_argument(
        "--enum-threshold",
        help="Threshold of unique items up to which enum categories should be populated in the JSON schema",
        type=int,
        default=DEFAULT_ENUM_THRESHOLD,
    )
    parser.add_argument(
        "--enum-fields",
        help="Forces a certain field to be classed as an enum, useful"
        " for including fields that do not meet `enum-threshold` criteria",
    )
    parser.add_argument(
        "--bound-types",
        help="""Types for which bounds should be encoded into the schema,
  default is numbers, for which minimum / maximum are determined. For strings
  minLength and maxLength are determined. Set `--bound-types=none` to disable
  bound detection""",
    )
    parser.add_argument(
        "--explicit-nulls",
        help="""By default, fields that have null and another type are typed
      as non-required with the non-null type. Another interpretation is to
      assume the field will be present and allow it to dual-typed with null.""",
        action="store_true",
    )
    parser.add_argument("-o", "--output", help="Save schema to file")
    args = parser.parse_args(cmd_args)
    enum_fields = [] if args.enum_fields is None else args.enum_fields.split(",")
    bound_types = (
        {"integer", "number"}
        if args.bound_types is None
        else set(args.bound_types.split(","))
    )
    if bound_types == ["none"]:
        bound_types = []
    res = infer_schema(
        args.filename,
        args.enum_threshold,
        enum_fields,
        bound_types,
        args.explicit_nulls,
    )
    output_schema = json.dumps(res, sort_keys=True, indent=2)
    if args.output:
        Path(args.output).write_text(output_schema)
    else:
        print(output_schema)


if __name__ == "__main__":
    main()
