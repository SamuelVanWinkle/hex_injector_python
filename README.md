# Hex Injector Tool

A Python utility for injecting user-defined serial numbers into Intel HEX firmware files.
The tool first verifies the a placeholder marker (0xAA55) at a known location (0x4000)

## Notes
- Although it was mentioned that the placeholder existed at the address 0x2000, it was found in the original file at 0x4000, so that address is the default location to be searched

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

## Sample input and output

python -m injector.main --input input.hex --address 0x4000 --serial A1B2C3D4 --output output.hex

Available space found: 11 bytes (22 hex characters)
Serial bytes to be injected: A1B2C3D4
Proceed with this serial? [y/N]: y
Parsed serial bytes: b'\xa1\xb2\xc3\xd4'
Planned changes (address : old -> new):
 0x4000 : 0x55 -> 0xd4
 0x4001 : 0xaa -> 0xc3
 0x4002 : 0x0 -> 0xb2
 0x4003 : 0x0 -> 0xa1
Successfully injected the serial number into the file.
Changes:
 0x4000 : 0xd4
 0x4001 : 0xc3
 0x4002 : 0xb2
 0x4003 : 0xa1

## Dependencies

- [`intelhex`](https://pypi.org/project/IntelHex/)
- [`argparse`](https://docs.python.org/3/library/argparse.html) (built-in)
- [`datetime`](https://docs.python.org/3/library/datetime.html) (built-in)
- [`re`](https://docs.python.org/3/library/re.html) (built-in)
- [`pytest`](https://pypi.org/project/pytest/) *(optional, for testing)*

Install dependencies using pip:

```bash
pip install intelhex pytest

