"""Shared application paths and platform helpers."""
import os
import sys
import subprocess
import webbrowser

APP_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(APP_DIR, "generated_qr")
HISTORY_FILE = os.path.join(APP_DIR, "history.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def open_path(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def open_url(url):
    webbrowser.open(url)
