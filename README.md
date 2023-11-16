# Infer schema

Infer JSON schema from CSV files.

## Installation

The best way to install is via `pipx`:

```shell
pipx install infer-schema
```

Currently, infer-schema is a single script without any external dependencies, so
you can download and move it to somewhere in your PATH (remember to set
executable bit using `chmod +x`).

## Usage

infer-schema should work out of the box with any CSV file. There are a few
options that help you to tune the schema detection based on the specifics of our
data.

* **`--enum-threshold`**: Threshold of unique items up to which enum categories
  should be populated in the JSON schema, default = 10
* **`--enum-fields`**: Forces a certain field to be classed as an enum, useful
  for including fields that do not meet `enum-threshold` criteria
* **`--bound-types`**: Types for which bounds should be encoded into the schema,
  default is numbers, for which minimum / maximum are determined. For strings
  minLength and maxLength are determined.Set `--bound-types=none` to disable
  bound detection
