import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

SDK_DIR = Path("C:/Users/John/android-sdk")
SDK_DIR.mkdir(parents=True, exist_ok=True)

ZIP_PATH = Path("C:/Users/John/cmdline-tools.zip")
URL = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"

print(f"Downloading Android Command Line Tools from {URL}...")
urllib.request.urlretrieve(URL, ZIP_PATH)
print("Download complete. Extracting zip...")

cmdline_base = SDK_DIR / "cmdline-tools"
cmdline_latest = cmdline_base / "latest"
cmdline_latest.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(cmdline_base)

# The zip extracts into cmdline-tools/cmdline-tools/...
# Move contents to cmdline-tools/latest/...
extracted_inner = cmdline_base / "cmdline-tools"
if extracted_inner.exists():
    for item in extracted_inner.iterdir():
        dest = cmdline_latest / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(item), str(cmdline_latest))
    shutil.rmtree(extracted_inner, ignore_errors=True)

if ZIP_PATH.exists():
    ZIP_PATH.unlink()

print(f"Android SDK tools successfully installed in {SDK_DIR}")
