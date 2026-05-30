import eel
import os
import ctypes
from model import init_driver, send_whatsapp_message
from startup import add_to_startup_and_run
from database import add_task

# Calcola il percorso assoluto della cartella 'web'
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
web_dir = os.path.join(base_dir, 'web')

# Inizializza l'interfaccia UI
eel.init(web_dir)

# Registra il demone all'avvio e fallo partire subito in background
add_to_startup_and_run()

def update_ui_status(message):
    """Richiama la funzione JS esposta per mostrare i log all'utente."""
    try:
        eel.update_ui_status(message)
    except Exception as e:
        print("Errore aggiornamento UI:", e)

@eel.expose
def minimize_window():
    """Minimizza la finestra dell'interfaccia usando le API di Windows."""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, "WhatsApp Auto Sender")
        if hwnd:
            user32.ShowWindow(hwnd, 6) # SW_MINIMIZE = 6
    except Exception as e:
        print("Errore durante la minimizzazione:", e)

@eel.expose
def start_whatsapp_automation(contact_name, message_text):
    """
    Metodo legacy per invio immediato (se necessario).
    """
    return send_whatsapp_message(contact_name, message_text, status_callback=update_ui_status)

@eel.expose
def schedule_task(contact_name, message_text, target_timestamp):
    """
    Salva il messaggio nel database in modo permanente.
    Il demone in background (scheduler.py) lo invierà al momento giusto.
    """
    try:
        add_task(contact_name, message_text, target_timestamp)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == '__main__':
    print("Avviando WhatsApp Bot UI...")
    try:
        # Prova ad aprire con Microsoft Edge (predefinito su Windows)
        eel.start('index.html', size=(500, 680), port=0, mode='edge')
    except EnvironmentError:
        print("Edge/Chrome non trovati in modalità App. Apro nel browser di sistema predefinito...")
        eel.start('index.html', size=(500, 680), port=0, mode='default')
    except Exception as e:
        print("Errore generico nell'avvio dell'app Eel:", e)
