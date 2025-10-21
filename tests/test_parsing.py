from injector.injector import is_valid_serial

def test_valid_serial_hex():
    # Ensures serial is valid
    assert is_valid_serial("ABC123")
    assert is_valid_serial("A1B2C3D4")
    assert not is_valid_serial("G12345")
    assert not is_valid_serial("A1 B2")

