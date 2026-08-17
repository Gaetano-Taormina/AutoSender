import os
import sys

def add_to_startup_and_run():
    """
    Creates a VBS script in the Windows startup folder to launch
    the background service at every PC boot, and launches it immediately.
    """
    if sys.platform != "win32":
        return
        
    try:
        startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        vbs_path = os.path.join(startup_dir, "AutoSender_Scheduler.vbs")
        
        pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
        scheduler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheduler.py")
        
        # The VBS executes pythonw (invisible) passing the scheduler script
        vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\n'
        vbs_content += f'WshShell.Run chr(34) & "{pythonw_path}" & chr(34) & " " & chr(34) & "{scheduler_path}" & chr(34), 0, False\n'
        
        # Write the file in the startup folder
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
            
        # Check if the scheduler is already running via Windows Mutex
        import ctypes
        kernel32 = ctypes.windll.kernel32
        
        # OpenMutexW returns a handle if it exists, 0 otherwise
        existing_mutex = kernel32.OpenMutexW(0x100000, False, "AutoSender_Scheduler_Mutex")
        if existing_mutex:
            kernel32.CloseHandle(existing_mutex)
            # Already running in background! Avoid spawning a new process and heating up CPU.
            return
            
        # Launch the service right now by executing the VBS file (detached) so it survives UI closure
        import subprocess
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen(
            ['wscript.exe', vbs_path], 
            creationflags=DETACHED_PROCESS, 
            close_fds=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except Exception as e:
        print(f"Cannot add service to startup: {e}")

if __name__ == "__main__":
    add_to_startup_and_run()
