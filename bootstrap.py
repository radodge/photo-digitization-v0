#!/usr/bin/env python3
"""
Minimal bootstrap for this repo:
- Create (or clear+recreate) ./.venv
- Upgrade core tooling inside the venv (pip/setuptools[/wheel])
- Install requirements.txt if present

Intended to be called by run.py when .venv isn't ready yet,
but it's safe to run manually any time.
"""
import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
from venv import EnvBuilder

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
REQS = ROOT / "requirements.txt"

def venv_python(venv_dir: Path) -> Path:
    return venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

def get_nvidia_drivers() -> list[str]:
    """Return detected NVIDIA driver version(s).

    Uses `nvidia-smi` if available. Returns an empty list if no NVIDIA driver
    or tool is detected. Multiple GPUs may report versions; the list is
    de-duplicated and sorted lexicographically.
    """
    smi = shutil.which("nvidia-smi")
    if not smi:
        return []

    versions: set[str] = set()

    # Preferred: structured CSV query
    try:
        out = subprocess.check_output(
            [smi, "--query-gpu=driver_version", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.search(r"\d+(?:\.\d+)+", line)
            if m:
                versions.add(m.group(0))
        if versions:
            return sorted(versions)
    except Exception:
        pass

    # Fallback: parse default nvidia-smi summary output
    try:
        out = subprocess.check_output([smi], text=True, stderr=subprocess.DEVNULL, timeout=5)
        for m in re.findall(r"Driver Version:\s*([0-9.]+)", out):
            versions.add(m)
    except Exception:
        pass

    return sorted(versions)

def _has_modern_nvidia(min_branch: int = 580) -> bool:
    vers = get_nvidia_drivers()
    for v in vers:
        try:
            major = int(v.split(".", 1)[0])
            if major >= min_branch:
                return True
        except ValueError:
            continue
    return False

def install_runtime_deps_with_extras(py_exe: str) -> None:
    extra = "gpu" if _has_modern_nvidia(580) else "cpu"
    try:
        subprocess.check_call([py_exe, "-m", "pip", "install", f".[{extra}]"])
    except subprocess.CalledProcessError:
        # Fallback to cpu extras
        subprocess.check_call([py_exe, "-m", "pip", "install", ".[cpu]"])

def _venv_site_packages(py_exe: str) -> Path:
    """Return the site-packages directory for the given Python executable."""
    try:
        out = subprocess.check_output(
            [py_exe, "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
            text=True,
        ).strip()
        if out:
            return Path(out)
    except Exception:
        pass
    # Fallback: try site.getsitepackages()[0]
    out = subprocess.check_output(
        [py_exe, "-c", "import site; print(site.getsitepackages()[0])"],
        text=True,
    ).strip()
    return Path(out)

def _install_sitecustomize(py_exe: str, src: Path | None = None) -> None:
    """Copy sitecustomize.py from repo root into venv site-packages if present."""
    src_path = src or (ROOT / "sitecustomize.py")
    if not src_path.exists():
        return
    dst_dir = _venv_site_packages(py_exe)
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src_path), str(dst_dir / "sitecustomize.py"))

def ensure_bootstrapped():
    exists = VENV.exists()
    is_venv = (VENV / "pyvenv.cfg").exists()

    if exists and not is_venv:
        print(f"Refusing to clear non-venv directory: {VENV}", file=sys.stderr)
        return 2, None

    # Create new venv, or clear+recreate if an actual venv already exists.
    EnvBuilder(
        with_pip=True,
        upgrade_deps=True,        # upgrades pip/setuptools[/wheel] inside the venv
        symlinks=(os.name != "nt"),
        clear=(exists and is_venv)
    ).create(str(VENV))

    py_exe = venv_python(VENV)

    install_runtime_deps_with_extras(str(py_exe))

    # Place sitecustomize.py into the environment (optional)
    _install_sitecustomize(str(py_exe))


    print("Bootstrap complete.")
    return 0, str(py_exe)

# if __name__ == "__main__":
#     sys.exit(ensure_bootstrapped())
