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

## Development

Install pre-commit to setup ruff linting and formatting.

To generate the man page, [scdoc](https://git.sr.ht/~sircmpwn/scdoc) is required:

```shell
scdoc < infer-schema.1.scd > infer-schema.1
```
