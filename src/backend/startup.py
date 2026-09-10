import os
import subprocess
import sys

# Ensure backend directory is in sys.path for standalone invocations
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def get_startup_vbs_path():
    """Returns the absolute path to AutoSender_Scheduler.vbs in the Windows Startup directory."""
    if sys.platform != "win32" or "APPDATA" not in os.environ:
        return None
    return os.path.join(
        os.environ["APPDATA"],
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
        "AutoSender_Scheduler.vbs",
    )


def remove_from_startup():
    """Removes the scheduler VBS from Windows Startup folder if present."""
    try:
        vbs_path = get_startup_vbs_path()
        if vbs_path and os.path.exists(vbs_path):
            os.remove(vbs_path)
            return True
    except Exception as e:
        print(f"Cannot remove service from startup: {e}")
    return False


def get_python_executable():
    """Finds the best python executable, preferring pythonw.exe if available."""
    executable = sys.executable
    if "python.exe" in executable.lower():
        idx = executable.lower().rfind("python.exe")
        candidate = executable[:idx] + "pythonw.exe"
        if os.path.exists(candidate):
            return candidate
    return executable


def add_to_startup_and_run():
    """
    Creates a robust VBS script in the Windows startup folder to launch
    the background service at every PC boot, and launches it immediately.
    """
    if sys.platform != "win32":
        return

    try:
        vbs_path = get_startup_vbs_path()
        if not vbs_path:
            return

        python_path = get_python_executable()
        scheduler_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "scheduler.py"
        )

        # The VBS safely executes pythonw/python (invisible) only if files exist, with error suppression
        vbs_content = "On Error Resume Next\n"
        vbs_content += 'Set WshShell = CreateObject("WScript.Shell")\n'
        vbs_content += 'Set fso = CreateObject("Scripting.FileSystemObject")\n'
        vbs_content += f'pyPath = "{python_path}"\n'
        vbs_content += f'scPath = "{scheduler_path}"\n'
        vbs_content += "If fso.FileExists(pyPath) And fso.FileExists(scPath) Then\n"
        vbs_content += '    WshShell.Run chr(34) & pyPath & chr(34) & " " & chr(34) & scPath & chr(34), 0, False\n'
        vbs_content += "End If\n"

        # Write the file in the startup folder
        os.makedirs(os.path.dirname(vbs_path), exist_ok=True)
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)

        # Check if the scheduler is already running via Windows Mutex
        import ctypes

        kernel32 = ctypes.windll.kernel32

        # OpenMutexW returns a handle if it exists, 0 otherwise
        existing_mutex = kernel32.OpenMutexW(
            0x100000, False, "AutoSender_Scheduler_Mutex"
        )
        if existing_mutex:
            kernel32.CloseHandle(existing_mutex)
            # Already running in background! Avoid spawning a new process and heating up CPU.
            return

        # Launch the service right now by executing the VBS file (detached) so it survives UI closure
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(
            ["wscript.exe", vbs_path],
            creationflags=DETACHED_PROCESS,
            close_fds=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    except Exception as e:
        print(f"Cannot add service to startup: {e}")


def sync_startup_with_pending():
    """
    Syncs Windows startup state with DB pending tasks:
    - If there are pending tasks, ensures startup VBS is registered and scheduler runs.
    - If there are no pending tasks, removes startup VBS to prevent unnecessary boots.
    """
    try:
        from database import get_pending_tasks

        pending = get_pending_tasks()
        if pending:
            add_to_startup_and_run()
        else:
            remove_from_startup()
    except Exception as e:
        print(f"Cannot sync startup: {e}")


if __name__ == "__main__":
    sync_startup_with_pending()

