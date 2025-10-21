from intelhex import IntelHex 
from datetime import datetime
import shutil
from pathlib import Path
from typing import Optional
import re

MAX_HEX_CHARS = 16 # allows up to 16 hex characters or 8 bytes
MARKER_LEN = 2 # The marker AA55 is 2 bytes
HEX_RE = re.compile(r'[0-9a-fA-F]+$')


def load_hex_file(path: str) -> IntelHex:
    """ 
    Loads the hex file and creates a backup
    Parameters: 
        path (str): The file to be opened
    Returns:
        IntelHex: The loaded file 
    Raises:
        ValueError if input file is not found
    """

    ih = IntelHex()
    try:
        ih.loadhex(path)
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {path}")    
    
    # Make a backup for security. 
    # The backup file is created with a timestamp. 
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup = Path(path).with_name(f"backup_{timestamp}.hex")
    shutil.copy(path, backup)

    return ih

def detect_endianness(ih: IntelHex, address: int, marker_value: int = 0xAA55, marker_len: int = 2) -> Optional[str]:
    """
    Verifies that the given marker is stored at the given address
    and checks for its endianness.

    Parameters:
        ih (IntelHex): An IntelHex instance that has already been loaded
        address (int): An integer representing the address of the marker
        marker_value (int): Expected placeholder value
        marker_len (int): number of bytes in the marker_value

    Returns:
        "big" if the bytes at the given address are stored using big-endian
        "little" if the bytes are stored using little-endian
        None if the marker is not found
    """

    # Create big-endian and little-endian bytes
    big_en = marker_value.to_bytes(marker_len, byteorder="big")
    little_en = big_en[::-1]

    # Try to read the bytes from image
    try:
        result = bytes(ih[address + i] for i in range(marker_len))
    except KeyError:
        # Address wasn't found
        return None
    
    if result == big_en:
        return "big"
    if result == little_en:
        return "little"
    # Could not determine if big or little endian 
    return None

def is_valid_serial(serial: str) -> bool:
    # Confirms the entered serial is valid
    return bool(HEX_RE.match(serial))

def parse_serial(s: str, max_chars: int = MAX_HEX_CHARS) -> bytes:
    """ 
    Parses the serial number, ensuring that it contains only valid characters
    and is less than the max length, reprompting the user if it is invalid.

    Parameters:
        s (str): The serial number in string format. Should contain only Hex Characters.
        max_chars (int): The maximum number of characters the hex is allowed.

    Returns: 
        The serial number converted to bytes for injection.

    Notes:
        If the serial is entered with 0x at the beginning or - the code will remove them. 
    """
    failed = False
    while True:
        if failed:
            s = input(f"Enter a serial number in hex up to {max_chars} chars: ").strip()
        if s.lower().startswith("0x"):
            s = s[2:]
        s = s.replace(" ", "").replace("-", "")

        if len(s) == 0:
            print("No input - Reenter serial number")
            failed = True
            continue
        if len(s) > max_chars:
            print(f"Serial too long: Must be {max_chars} or less")
            failed = True
            continue
        if len(s) % 2 != 0:
            print("Serial number must have an even number of digits")
            failed = True
            continue
        if not is_valid_serial(s):
            print(f"An invalid character was entered. Must include only hex values (0-9, A-F)")
            failed = True
            continue

        try:
            b = bytes.fromhex(s)
        except ValueError:
            print("Failed to parse hex. Please re-enter")
            failed = True
            continue

        print(f"Serial bytes to be injected: {b.hex().upper()}")
        confirm = input("Proceed with this serial? [y/N]: ").strip().lower()
        if confirm in ("y", "yes"):
            return b
        print("Please re-enter the serial number")
        failed = True

def get_max_payload_len(ih: IntelHex, start_addr: int, padding_byte: int = 0x00, max_scan: int = 256) -> int:
    """ 
    Checks the hex file at the given start address and determines 
    the amount of free space that can be used for the serial number.

    Parameters:
        ih (IntelHex): An IntelHex instance that has already been loaded
        start_addr (int): The start address of the marker.
        padding_bytes (int): Assumes that bytes 0x00 are empty data that can be used
        for entering the serial number, unless overwritten.
        max_scan (int): The maximum number of bytes to scan
    """
    length = 0
    for i in range(max_scan):
        addr = start_addr + i
        try:
            b = ih[addr]
        except KeyError:
            # Missing address - stop scanning.
            break

        # If a non-padding byte is found, stop
        if i >= MARKER_LEN and b != padding_byte: 
            break
        length += 1
    return length


def inject_and_verify_serial(ih: IntelHex, 
                             address: int, 
                             data: bytes, 
                             out_path: str) -> bool: 
    """ 
    Injects the serial number bytes into the hex file and verifies
    that the injection was successful
    
    Parameters:
        ih (IntelHex): An IntelHex instance that has already been loaded
        address (int): The starting address of the marker
        data (bytes): The serial number in bytes to be injected
        out_path (str): The output path
    
    Returns:
        True if the verification was successful
    """
    for i in range(len(data)):
        ih[address + i] = data[i]
    try:
        ih.write_hex_file(out_path)
    except Exception as e:
        raise RuntimeError(f"Failed to write output file {out_path} : {e}")
    
    try: 
        ih2 = IntelHex()
        ih2.loadhex(out_path)
    except Exception as e:
        raise RuntimeError(f"Failed to reload written hex.")
    
    unexpected_bytes = []
    for i, b in enumerate(data):
        addr = address + i
        try:
            got = ih2[addr]
        except KeyError:
            unexpected_bytes.append((addr, b, None))
            continue
        if got != b:
            unexpected_bytes.append((addr, b, got))

    # If any unexpected bytes are found, raise error
    if unexpected_bytes:
        raise RuntimeError(f"Verification failed.")
    
    return True

    
