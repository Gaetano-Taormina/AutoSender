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
        
        # Check if we are running as a PyInstaller executable
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            # When frozen, the executable is the program itself, pass the "scheduler" argument
            vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\n'
            vbs_content += f'WshShell.Run chr(34) & "{exe_path}" & chr(34) & " scheduler", 0, False\n'
        else:
            pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
            scheduler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheduler.py")
            
            # The VBS executes pythonw (invisible) passing the scheduler script
            vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\n'
            vbs_content += f'WshShell.Run chr(34) & "{pythonw_path}" & chr(34) & " " & chr(34) & "{scheduler_path}" & chr(34), 0, False\n'
        
        # Write the file in the startup folder
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
            
        # Launch the service right now by executing the VBS file (this prevents the parent PyInstaller from locking the _MEI temp folders)
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
