import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VBS_PATH = BASE_DIR / "scripts" / "start_backend_silent.vbs"

# Windows Startup Folder Path
STARTUP_FOLDER = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
SHORTCUT_PATH = STARTUP_FOLDER / "FormFill_AI_Backend.vbs"

def install_autostart():
    print("=" * 60)
    print("[+] INSTALLING FORMFILL AI BACKGROUND AUTO-START SERVICE")
    print("=" * 60)

    # Copy VBS script to Windows Startup folder
    with open(VBS_PATH, "r", encoding="utf-8") as f_src:
        content = f_src.read()

    with open(SHORTCUT_PATH, "w", encoding="utf-8") as f_dst:
        f_dst.write(content)

    print(f"[OK] Auto-Start Script Installed to Windows Startup Folder:")
    print(f"     {SHORTCUT_PATH}")

    # Register Task Scheduler task for instant startup
    task_name = "FormFill_AI_Backend_Service"
    cmd = [
        "schtasks", "/create", "/tn", task_name,
        "/tr", f'wscript.exe "{SHORTCUT_PATH}"',
        "/sc", "onlogon",
        "/rl", "HIGHEST",
        "/f"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[OK] Windows Task Scheduler Service Registered: '{task_name}'")
    else:
        print(f"[INFO] Windows Task Scheduler Status: {res.stdout or res.stderr}")

    print("\n[SUCCESS] SETUP COMPLETE!")
    print("FormFill AI backend server will now run automatically in the background")
    print("every time Windows starts up! You never have to manually open terminal or run commands again.")
    print("=" * 60)

if __name__ == "__main__":
    install_autostart()
