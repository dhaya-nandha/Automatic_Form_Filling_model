import subprocess
import os
from pathlib import Path

SDKMANAGER = "C:/Users/John/android-sdk/cmdline-tools/latest/bin/sdkmanager.bat"
SDK_DIR = "C:/Users/John/android-sdk"

os.environ["ANDROID_HOME"] = SDK_DIR
os.environ["ANDROID_SDK_ROOT"] = SDK_DIR

print("Accepting Android SDK licenses and installing packages...")

# Accept licenses
licenses_proc = subprocess.Popen(
    [SDKMANAGER, "--sdk_root=" + SDK_DIR, "--licenses"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
out, err = licenses_proc.communicate(input="y\ny\ny\ny\ny\ny\ny\ny\ny\ny\n")
print(out[:500])

# Install platforms;android-34 build-tools;34.0.0 platform-tools
cmd = [
    SDKMANAGER,
    "--sdk_root=" + SDK_DIR,
    "platforms;android-34",
    "build-tools;34.0.0",
    "platform-tools"
]
print("Running:", " ".join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
print("Return code:", res.returncode)
