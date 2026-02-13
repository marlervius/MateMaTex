"""
Test configuration — ensures backend/app is importable as `app`.
"""
import sys
from pathlib import Path

# Add backend/ to path so `from app.X` works in tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
