"""
Android APK Build Helper & Packaging Script for Automatic Form-Filling Mobile App.
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def generate_apk_instructions():
    print("=" * 70)
    print("📱 ANDROID APK BUILD & DEPLOYMENT GUIDE")
    print("=" * 70)
    print("\nOption 1: Progressive Web App (PWA) / Instant Android App (Zero Build)")
    print("  1. Run backend server: `uvicorn backend.app:app --host 0.0.0.0 --port 8000`")
    print("  2. Open Chrome on your Android phone and navigate to `http://<YOUR_COMPUTER_IP>:8000`")
    print("  3. Tap Chrome Menu (3 dots) -> Select 'Add to Home Screen' / 'Install App'")
    print("  -> Your app installs directly onto your Android device as an app icon!")

    print("\nOption 2: Build Native Standalone APK (Capacitor / Android Studio)")
    print("  1. Install Node.js & Capacitor CLI: `npm i -g @capacitor/cli @capacitor/core`")
    print("  2. Initialize Capacitor in `mobile_app`: `npx cap init 'FormFill AI' 'com.formfill.ai'`")
    print("  3. Add Android platform: `npx cap add android`")
    print("  4. Copy web assets: `npx cap copy`")
    print("  5. Build APK: `npx cap open android` (or run `gradlew assembleDebug` inside android folder)")
    print("  -> Generates `app-debug.apk` ready for installation on any Android phone!")
    print("=" * 70)

if __name__ == "__main__":
    generate_apk_instructions()
