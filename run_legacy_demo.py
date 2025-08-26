"""
Simple launcher for the legacy photo digitization app.

- Creates required folders (Ingest, Processed Photos, Debug Output)
- Starts the legacy_main_processing entrypoint

Usage:
  python run_legacy_demo.py
"""

from app.main_processing import main

if __name__ == "__main__":
    main()
