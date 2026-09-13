import os
import sys
import urllib.request
import subprocess
from pathlib import Path

CF_EXE = Path("C:/Users/John/cloudflared.exe")

if not CF_EXE.exists():
    print("Downloading Cloudflare Tunnel binary...")
    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    urllib.request.urlretrieve(url, CF_EXE)
    print("Cloudflare Tunnel downloaded!")

print("Starting Cloudflare Tunnel on port 5000...")
proc = subprocess.Popen([str(CF_EXE), "tunnel", "--url", "http://127.0.0.1:5000"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

for line in proc.stdout:
    print(line, end="")
    if "trycloudflare.com" in line:
        print("\n" + "="*60)
        print("YOUR LIVE MOBILE HTTPS URL:")
        for word in line.split():
            if "trycloudflare.com" in word:
                print(word)
        print("="*60 + "\n")
        break
