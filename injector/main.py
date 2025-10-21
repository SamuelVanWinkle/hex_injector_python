from intelhex import IntelHex
from injector.injector import load_hex_file, get_max_payload_len, inject_and_verify_serial, parse_serial, detect_endianness
import sys
import argparse

def parse_address(s: str) -> int:
    """
    Converts the entered address into an integer, ensuring it is valid
    """
    try: 
        v = int(s, 0)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid Address: {s}")
    if v < 0:
        raise argparse.ArgumentTypeError("Address must be non-negative")
    return v

def main():
    """
    The entry point for the hex injector
    """
    parser = argparse.ArgumentParser(description="Process serial number and backup path.")
    parser.add_argument("--serial", type=str, required=True, help="The serial number in hex")
    parser.add_argument("--input", type=str, required=True, help="The path to the input HEX file")
    parser.add_argument("--address", type=parse_address, default=0x4000, help="The address of the injection. Defaults = 0x4000")
    parser.add_argument("--padding_bytes", type=int, default = 0x00, help="Defines the padding bytes used. Default = 0x00")
    parser.add_argument("--output", type=str, required=True, help="The output file path")

    args = parser.parse_args()

    # First loads the hex file and creates a backup.
    ih = load_hex_file(args.input) 
    
    endian = detect_endianness(ih, args.address, 0xAA55 , 2)
    if endian == None:
        print("Placeholder was not found - exiting")
        sys.exit(1)
    
    payload_start = args.address + 2 # Skips the 2-byte marker.

    max_len = get_max_payload_len(ih, payload_start, max_scan=64)

    if max_len == 0:
        print("No space available after marker.")
        sys.exit(1)

    print(f"Available space found: {max_len} bytes ({max_len * 2} hex characters)")

    serial_bytes = parse_serial(args.serial, max_len)
    print(f"Parsed serial bytes: {serial_bytes}")

    endian_serial_bytes = serial_bytes
    if endian == "little":
        endian_serial_bytes = serial_bytes[::-1]

    # Before injecting displays the changes that will be made
    print("Planned changes (address : old -> new):")
    for i in range(len(endian_serial_bytes)):
        addr = args.address + i
        old = ih[addr] if addr in ih.addresses() else None
        new = endian_serial_bytes[i]
        print(f" {hex(addr)} : {None if old is None else hex(old)} -> {hex(new)}")

    success = inject_and_verify_serial(ih, args.address, endian_serial_bytes, args.output)

    if success:
        print(f"Successfully injected the serial number into the file.\nChanges:")
        for i in range(len(endian_serial_bytes)):
            addr = args.address + i
            new = ih[addr] if addr in ih.addresses() else None
            print(f" {hex(addr)} : {None if new is None else hex(new)}")

if __name__ == "__main__":
    main()