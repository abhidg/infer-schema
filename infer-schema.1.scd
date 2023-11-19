infer-schema(1)

# NAME

infer-schema - generate JSON Schema from CSV files

# SYNOPSIS

*infer-schema* file [options]

# DESCRIPTION

The infer-schema utility generates JSON Schema (draft 7) corresponding to a CSV
file, such that the CSV file is valid against the generated schema. The JSON
Schema is shown on standard output and can be piped or written to a file with
the *--output* option.

The following options are available:

*-h*, *--help*
	Show usage information

*--enum-threshold* _threshold_
	The _threshold_ of unique items up to which enum categories should be
	populated in the JSON schema. Default threshold is 10.

*--enum-fields* _fields_
	Forces _fields_ (comma-separated) to be classed as an enum, useful for
	including fields that do not meet enum _threshold_ criteria

*--bound-types* _types_
	Comma-separated _types_ for which bounds should be encoded into the schema,
	default is 'number,integer', for which minimum / maximum are determined. For
	strings minLength and maxLength are determined. Set *--bound-types*=none to
	disable bound detection. Allowed bound types are *integer*, *number* and
	*string*

*--explicit-nulls*
	By default, fields that have null and another type are typed as non-required
	with the non-null type. This setting makes the nulls explicit by dual typing
	a field with the non-null type.

	As an example, consider a field 'count' that has the following values
	20,NA,30. By default, this field will be typed as 'integer' and will not be
	required. With *--explicit-nulls* set, this will be typed as [integer, null]

*-o* _output_, *--output* _output_
	Save schema to _output_ file

# EXAMPLES

Given this CSV file called _dates.csv_

```
date,num_cases
2022-11-11,4
2022-11-12,5
2022-11-13,6
,10
2022-11-15,10
2022-11-16,5
2022-11-17,3
2022-11-18,2
2022-11-19,10
2022-11-20,11
2022-11-21,4
2022-11-22,20
2022-11-23,
2022-11-24,9
2022-11-25,4
2022-11-26,21
2022-11-27,99
2022-11-28,59
2022-11-30,45
```

Running 'infer-schema dates.csv' gives the following output

```
{
	"$schema": "https://json-schema.org/draft-07/schema",
	"description": "Description of tests/dates.csv",
	"properties": {
		"date": {
			"description": "Description for column date",
			"format": "date",
			"type": "string"
		},
		"num_cases": {
			"description": "Description for column num_cases",
			"maximum": 99,
			"minimum": 2,
			"type": "integer"
		}
	},
	"required": [],
	"title": "JSON Schema for tests/dates.csv"
}
```

Here we see that infer-schema determines minimum and maximum values for integer
columns. For strings, minLength and maxLength are determined. This is controlled
by the *--bound-types* setting, which can be set to *none* to turn off bounds
detection.

By default, any column with upto 10 (default *--enum-threshold*) unique values
is considered categorical and expressed as a JSON Schema enum type. Columns with
more than 10 values can be forced to be of enum type by using *--enum-fields*.

# BUGS

Report bugs at https://github.com/abhidg/infer-schema/issues
