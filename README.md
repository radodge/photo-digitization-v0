# Photo Digitization Application v0 - Legacy Demo
> *Version 1 of the application is in active development. The codebase lives in a private repository to safeguard intellectual property.*
## Overview
This repository contains a legacy prototype of my photo 'digitization' application. Follow the setup guide if you'd like to try the application for yourself.


## Usage Guide
### Prerequisites
- Python 3.10+
### Step 1 - Clone the repository
Navigate to any folder in your system and clone the repository.
```bash
git clone https://github.com/radodge/photo-digitization-v0.git
cd photo-digitization-v0
```

### Step 2 - Create a virtual environment
This step is done to protect your system Python environment. Python packages installed by my setup script will be installed to `~/.venv/Lib/site-packages` instead of `C:/Program Files/Python313/Lib/site-packages`.

From this folder in PowerShell:

```powershell
python -m venv .venv                # Creates a virtual environment
.venv/Scripts/Activate.ps1          # Activates the virtual environment
python -m pip install --upgrade pip # Upgrades venv's package installer
pip install -r requirements.txt
```

### Launch

```powershell
python run_legacy_demo.py
```

What happens:
- App creates these folders if missing: `Ingest`, `Processed Photos`, `Debug Output`.
- A background watcher monitors `Ingest` for new images.

### Try it

Drop an image into `Ingest` (supported: .tif/.tiff/.png/.jpg/.jpeg/.bmp/.heic/.webp). The app will:
1) Auto-split the composite into subphotos.
2) Let you preview and confirm.
3) Save subphotos into `Processed Photos` (HEIC and JPEG by default) and inject metadata if ExifTool is available.

Tip: In Debug mode, use the menu Debug → Simulate Ingest File to trigger processing with existing files in `Ingest`.

### Notes

- CUDA is disabled by default. Enable in `legacy_main_processing.py` if your OpenCV build supports CUDA.
- HEIC read/write handled via `pillow-heif`.
- Metadata injection is skipped gracefully when ExifTool is not installed.