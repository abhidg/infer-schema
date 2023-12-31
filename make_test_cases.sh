#!/bin/sh
python3 infer_schema.py tests/mtcars.csv -o tests/mtcars.schema.json
python3 infer_schema.py tests/mtcars_partial.csv -o tests/mtcars_partial.schema.json
python3 infer_schema.py tests/mtcars_partial.csv \
  --enum-fields car_model -o tests/mtcars_partial_enum-fields.schema.json
python3 infer_schema.py tests/mtcars_partial.csv \
  --enum-threshold 30 -o tests/mtcars_partial_enum-threshold.schema.json
python3 infer_schema.py tests/mtcars_partial.csv \
  --explicit-nulls -o tests/mtcars_partial_explicit-nulls.schema.json
python3 infer_schema.py tests/mtcars_partial.csv \
  --bound-types=string -o tests/mtcars_partial_bound-string.schema.json
# dates and times
python3 infer_schema.py tests/dates.csv -o tests/dates.schema.json
python3 infer_schema.py tests/date-times.csv -o tests/date-times.schema.json
