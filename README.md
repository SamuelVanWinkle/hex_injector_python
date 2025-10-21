# Hex Injector Tool

A Python utility for injecting user-defined serial numbers into Intel HEX firmware files.
The tool first verifies the a placeholder marker (0xAA55) at a known location (0x4000)

## Features

- Accepts Intel HEX files
- Creates a backup of the file for safety
- Verifies that the placeholder exists and determines endianness
- Injects a user-defined serial number safely into the correct memory address
- Uses a CLI interface with helpful error messages

## Commands

--serial (REQUIRED) : The serial number in hex format (Ex: --serial A1B2C3D4)
--input (REQUIRED) : The input hex file (Ex: --input CrystalFontz_04.production.hex)
--address : The address of the placeholder marker. 0x4000 by default
--padding_bytes : Determines the padding bytes that are used. 0x00 by default
--output (REQUIRED) : The output path (Ex: --output output.hex)

## Dependencies

- [`intelhex`](https://pypi.org/project/IntelHex/)
- [`argparse`](https://docs.python.org/3/library/argparse.html) (built-in)
- [`datetime`](https://docs.python.org/3/library/datetime.html) (built-in)
- [`re`](https://docs.python.org/3/library/re.html) (built-in)
- [`pytest`](https://pypi.org/project/pytest/) *(optional, for testing)*

Install dependencies using pip:

```bash
pip install intelhex pytest

