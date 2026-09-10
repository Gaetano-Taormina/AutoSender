import ctypes
import sys
from unittest.mock import MagicMock

# Polyfill ctypes.windll on non-Windows platforms (e.g. Linux CI)
if not hasattr(ctypes, "windll"):
    ctypes.windll = MagicMock()
