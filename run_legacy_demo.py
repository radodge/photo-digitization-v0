#!/usr/bin/env python3
"""
Order of operations:
1) Ensure the virtual environment exists (by calling bootstrap.py if needed)
2) Run app.main_processing.main() using the venv's Python
"""
import os
import sys
import subprocess
from pathlib import Path
from bootstrap import ensure_bootstrapped

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    ret, py_exe = ensure_bootstrapped()
    if ret != 0:
        sys.exit(ret)
    # Invoke the console script installed by [project.scripts]
    scripts_dir = Path(py_exe).parent
    exe_name = "run_app.exe" if os.name == "nt" else "run_app"
    script_path = scripts_dir / exe_name

    if script_path.exists():
        subprocess.check_call([str(script_path), *sys.argv[1:]])
    else:
        # Fallback: import and run directly
        subprocess.check_call([
            py_exe,
            "-c",
            "import app.main_processing as m; m.main()",
            *sys.argv[1:]
        ])

