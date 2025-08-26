import os
import sys
from pathlib import Path

# Ensure CUDA (cu13) and cuDNN DLLs are visible to the loader on Windows.

_DLL_DIR_HANDLES = []  # keep handles alive for process lifetime

def _add_dir(p: Path) -> None:
    if not p.exists() or not p.is_dir():
        return
    try:
        if hasattr(os, "add_dll_directory"):
            h = os.add_dll_directory(str(p))  # Python 3.8+
            try:
                _DLL_DIR_HANDLES.append(h)
            except Exception:
                pass
        else:
            os.environ["PATH"] = str(p) + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass

def _add_tree(root: Path) -> None:
    if not root.exists():
        return
    candidates = set()
    # Core locations
    candidates.update({root, root / "bin", root / "bin" / "x86_64"})
    # First-level children common bins
    try:
        for child in root.iterdir():
            if child.is_dir():
                candidates.update({child, child / "bin", child / "bin" / "x86_64"})
    except Exception:
        pass
    # Any folder that actually contains DLLs under this root
    try:
        for dll in root.rglob("*.dll"):
            candidates.add(dll.parent)
    except Exception:
        pass
    for d in sorted(candidates):
        _add_dir(d)

site_pkgs = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
_add_tree(site_pkgs / "cu13")
_add_tree(site_pkgs / "cudnn")