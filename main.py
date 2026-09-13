import os
import sys
import uvicorn
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

if __name__ == "__main__":
    print("Starting FormFill AI Server on 0.0.0.0:5000...")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=5000, reload=False)
