import pytest
from intelhex import IntelHex
from injector.injector import inject_and_verify_serial

@pytest.fixture
def dummy_hex(tmp_path):
    # Create a small dummy IntelHex object with the placeholder
    ih = IntelHex()
    ih[0x2000] = 0xAA
    ih[0x2001] = 0x55
    file_path = tmp_path / "dummy.hex"
    ih.write_hex_file(file_path)
    return file_path

def test_injection_replaces_placeholder(dummy_hex, tmp_path):
    # Tests if injection successfully replaces the placeholder
    output_path = tmp_path / "out.hex"
    serial_number_bytes = bytes.fromhex("A1B2C3D4")

    inject_and_verify_serial(
        ih = IntelHex(),
        address=0x2000,
        data = serial_number_bytes,
        out_path=str(output_path)
    )

    ih_out = IntelHex()
    ih_out.loadhex(str(output_path))
    assert ih_out[0x2000] == 0xA1
    assert ih_out[0x2001] == 0xB2
    assert ih_out[0x2002] == 0xC3
    assert ih_out[0x2003] == 0xD4