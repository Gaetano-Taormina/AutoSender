import time
import os
import sys
import ctypes

# Aggiungi il percorso per importare correttamente dal pacchetto python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_pending_tasks, mark_task_done
from model import send_whatsapp_message

def run_scheduler():
    """Loop infinito che controlla i task pendenti in background."""
    # Evitiamo che ci siano 2 scheduler aperti contemporaneamente usando un Mutex di Windows
    mutex_name = "WhatsAppBot_Scheduler_Mutex"
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    if kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        sys.exit(0) # Lo scheduler sta già girando in background, chiudiamo questo duplicato
        
    while True:
        try:
            tasks = get_pending_tasks()
            now = time.time()
            
            for task in tasks:
                if now >= task["timestamp"]:
                    # Il momento è arrivato! Eseguiamo l'invio
                    contact = task["contact"]
                    message = task["message"]
                    task_id = task["id"]
                    
                    try:
                        # Chiamata alla funzione core (senza callback UI perché siamo in background)
                        result = send_whatsapp_message(contact, message, status_callback=None)
                        if result.get("success"):
                            mark_task_done(task_id, success=True)
                        else:
                            mark_task_done(task_id, success=False, error=result.get("error"))
                    except Exception as e:
                        mark_task_done(task_id, success=False, error=str(e))
        except Exception as e:
            pass # Ignora gli errori di rete o IO per evitare che il demone muoia
            
        time.sleep(30) # Controlla il file ogni 30 secondi

if __name__ == "__main__":
    run_scheduler()
