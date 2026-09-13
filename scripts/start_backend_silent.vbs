' Silent VBScript Launcher for FormFill AI Backend Server & Tunnel
' Runs python main.py and cloudflared invisibly in the background without opening any command window.

Set WshShell = CreateObject("WScript.Shell")
strProjectDir = "C:\Users\John\OneDrive\Documents\Desktop\dl project"

' 1. Start Python FastAPI Server (main.py) silently
WshShell.Run "cmd /c cd /d """ & strProjectDir & """ && python main.py", 0, False

' 2. Wait 3 seconds for server startup
WScript.Sleep 3000

' 3. Start Cloudflare Tunnel silently
WshShell.Run "cmd /c C:\Users\John\cloudflared.exe tunnel --url http://127.0.0.1:5000", 0, False
