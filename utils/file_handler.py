"""
File Handler Module
Provides safe, cross-platform file reading and writing utilities.
"""

from pathlib import Path
from typing import Union

def read_text_file(filepath: Union[str, Path]) -> str:
    """
    Reads and returns the contents of a text file using UTF-8 encoding.
    Raises FileNotFoundError if file does not exist.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: '{filepath}'")

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")

def write_text_file(filepath: Union[str, Path], content: str) -> str:
    """
    Writes text content to the specified file path. Creates parent directories if needed.
    Returns the resolved file path string.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path.resolve())
