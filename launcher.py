import os
import sys
import time
import threading
import webbrowser
import subprocess
import multiprocessing

# CRITICO: Esto evita el loop infinito en Windows con PyInstaller
if __name__ == "__main__":
    multiprocessing.freeze_support()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def find_streamlit():
    python_dir = os.path.dirname(sys.executable)
    candidates = [
        os.path.join(python_dir, "streamlit.exe"),
        os.path.join(python_dir, "Scripts", "streamlit.exe"),
        os.path.join(python_dir, "streamlit"),
        os.path.join(python_dir, "Scripts", "streamlit"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def open_browser():
    time.sleep(4)
    webbrowser.open("http://localhost:8501")

def main():
    app_path = resource_path("app.py")

    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    streamlit_path = find_streamlit()

    if streamlit_path:
        cmd = [streamlit_path, "run", app_path]
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", app_path]

    cmd += [
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "dark",
    ]

    # CRITICO: creationflags evita que Windows abra nuevas ventanas por cada proceso hijo
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    subprocess.run(cmd, **kwargs)

if __name__ == "__main__":
    main()
