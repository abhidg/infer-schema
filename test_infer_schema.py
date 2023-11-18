import json
import copy
import csv
import unittest
from typing import Dict, Any, Union, List
from infer_schema import infer_schema, NULL_VALUES

import fastjsonschema

TEST_CASES = [
    ("tests/mtcars.csv", "tests/mtcars.schema.json", dict()),
    ("tests/mtcars_partial.csv", "tests/mtcars_partial.schema.json", dict()),
    (
        "tests/mtcars_partial.csv",
        "tests/mtcars_partial_enum-fields.schema.json",
        dict(enum_fields=["car_model"]),
    ),
    (
        "tests/mtcars_partial.csv",
        "tests/mtcars_partial_enum-threshold.schema.json",
        dict(enum_threshold=30),
    ),
    (
        "tests/mtcars_partial.csv",
        "tests/mtcars_partial_bound-types.schema.json",
        dict(bound_types=set()),
    ),
]


def read_json(file: str) -> Dict[str, Any]:
    with open(file) as fp:
        return json.load(fp)


def is_numeric_jsonschema_type(t: Union[str, List[str]]) -> bool:
    t = {t} if isinstance(t, str) else set(t)
    return "string" not in t and (t & {"number"})


def is_integer_jsonschema_type(t: Union[str, List[str]]) -> bool:
    t = {t} if isinstance(t, str) else set(t)
    return t - {"null"} == {"integer"}


def casted_row(
    row: Dict[str, Any],
    integer_columns: List[str],
    numeric_columns: List[str],
    explicit_nulls: bool = False,
) -> Dict[str, Any]:
    nrow = copy.deepcopy(row)
    for c in row:
        if row[c] in NULL_VALUES:
            if explicit_nulls:
                nrow[c] = None
            else:
                del nrow[c]
            continue
        if c in integer_columns:
            nrow[c] = int(row[c])
        if c in numeric_columns:
            nrow[c] = float(row[c])
    return nrow


def validate_csv(file: str, jsonschema_file: str, explicit_nulls: bool = False) -> bool:
    jsonschema = read_json(jsonschema_file)
    numeric_columns = [
        c
        for c in jsonschema["properties"]
        if is_numeric_jsonschema_type(jsonschema["properties"][c].get("type", "string"))
        or isinstance(jsonschema["properties"][c].get("enum", ["x"])[0], float)
    ]
    integer_columns = [
        c
        for c in jsonschema["properties"]
        if is_integer_jsonschema_type(jsonschema["properties"][c].get("type", "string"))
        or isinstance(jsonschema["properties"][c].get("enum", ["x"])[0], int)
    ]

    validate = fastjsonschema.compile(jsonschema)
    with open(file) as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            try:
                validate(
                    casted_row(
                        row,
                        integer_columns,
                        numeric_columns,
                        explicit_nulls=explicit_nulls,
                    )
                )
            except fastjsonschema.JsonSchemaException as e:
                print(e.message)
                return False
    return True


class InferSchemaTest(unittest.TestCase):
    def test_infer_schema(self):
        for i, case in enumerate(TEST_CASES):
            with self.subTest(i=i):
                self.assertEqual(infer_schema(case[0], **case[2]), read_json(case[1]))


class ValidationTest(unittest.TestCase):
    def test_validation(self):
        for i, case in enumerate(TEST_CASES):
            with self.subTest(i=i):
                self.assertEqual(validate_csv(case[0], case[1]), True)
        # explicit nulls case
        self.assertEqual(
            validate_csv(
                "tests/mtcars_partial.csv",
                "tests/mtcars_partial_explicit-nulls.schema.json",
                explicit_nulls=True,
            ),
            True,
        )
