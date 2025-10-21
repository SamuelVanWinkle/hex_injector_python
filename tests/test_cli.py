import subprocess
from pathlib import Path

def test_cli_help_displays(tmp_path):
    # Shows the help output for the CLI
    result = subprocess.run(
        ["python", "-m", "injector.main", "--help"],
        capture_output=True, text=True
    )
    assert "usage" in result.stdout.lower()