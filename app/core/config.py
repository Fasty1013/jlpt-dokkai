"""Application-wide paths and constants (Step 8b)."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = os.path.join(str(PROJECT_ROOT), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
