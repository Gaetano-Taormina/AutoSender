import os
import sys

def add_to_startup_and_run():
    """
    Crea uno script VBS nella cartella di avvio automatico di Windows per lanciare
    il demone invisibile a ogni accensione del PC, e lo lancia immediatamente.
    """
    if sys.platform != "win32":
        return
        
    try:
        startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        vbs_path = os.path.join(startup_dir, "WhatsAppBot_Scheduler.vbs")
        
        pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
        scheduler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheduler.py")
        
        # Il VBS esegue pythonw (invisibile) passandogli lo script dello scheduler
        vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\n'
        vbs_content += f'WshShell.Run chr(34) & "{pythonw_path}" & chr(34) & " " & chr(34) & "{scheduler_path}" & chr(34), 0, False\n'
        
        # Scrive il file nell'avvio automatico
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
            
        # Avvia immediatamente lo script VBS così non bisogna riavviare il PC per attivare lo scheduler
        os.system(f'wscript.exe "{vbs_path}"')
        
    except Exception as e:
        print(f"Impossibile aggiungere il demone all'avvio: {e}")

if __name__ == "__main__":
    add_to_startup_and_run()
