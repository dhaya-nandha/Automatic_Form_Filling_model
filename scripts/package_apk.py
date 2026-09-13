import shutil
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APK_SRC = BASE_DIR / "android" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
APK_DEST = BASE_DIR / "FormFill_AI.apk"

def copy_apk():
    print("Waiting for APK build output...")
    for _ in range(60):
        if APK_SRC.exists():
            shutil.copyfile(APK_SRC, APK_DEST)
            print(f"✅ SUCCESS! APK packaged at: {APK_DEST}")
            print(f"Size: {APK_DEST.stat().st_size / (1024*1024):.2f} MB")
            return True
        time.sleep(2)
    print("APK source not found yet.")
    return False

if __name__ == "__main__":
    copy_apk()
