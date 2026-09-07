"""Compatibility entry point for hash-backed, cross-surface checks."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("validate_verified_snapshot.py")), run_name="__main__")
