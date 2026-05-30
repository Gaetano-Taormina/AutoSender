import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.service import Service as EdgeService

def init_driver():
    """Inizializza il webdriver utilizzando esclusivamente Microsoft Edge."""
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir)) # Risale da assets/python alla cartella principale
    
    # Usa AppData/Local per il profilo per evitare che OneDrive blocchi i file del database (storage denied)
    local_appdata = os.environ.get('LOCALAPPDATA', root_dir)
    profile_dir = os.path.join(local_appdata, "WhatsAppBot_Profile")
    options.add_argument(f"user-data-dir={profile_dir}")
    
    # Controlla se l'utente ha scaricato manualmente msedgedriver.exe nella cartella principale
    driver_path = os.path.join(root_dir, 'msedgedriver.exe')
    
    if os.path.exists(driver_path):
        service = EdgeService(executable_path=driver_path)
        driver = webdriver.Edge(service=service, options=options)
    else:
        # Fallback a Selenium Manager se il file non c'è (potrebbe dare errore di rete)
        driver = webdriver.Edge(options=options)
        
    return driver

def send_whatsapp_message(contact_name, message, status_callback=None):
    """
    Core logic per l'invio del messaggio su WhatsApp Web.
    status_callback è una funzione per aggiornare l'interfaccia UI.
    """
    driver = None
    try:
        if status_callback:
            status_callback("Apertura del browser in corso...")
            
        driver = init_driver()
        driver.get("https://web.whatsapp.com/")
        
        if status_callback:
            status_callback("In attesa di WhatsApp Web (scansiona il QR code se richiesto)...")
            
        # Attendiamo il login (fino a 120 secondi). L'elemento 'side' indica successo.
        wait = WebDriverWait(driver, 120)
        wait.until(EC.presence_of_element_located((By.ID, "side")))
        
        if status_callback:
            status_callback("Login confermato. Attesa caricamento chat...")
            
        # Aspettiamo un po' perché dopo il login c'è la schermata 'Caricamento delle tue chat...'
        time.sleep(10)
        
        # Premiamo il tasto ESCAPE sulla pagina per chiudere automaticamente eventuali 
        # popup, widget o notifiche fastidiose (come le 'Novità' di WhatsApp)
        try:
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
        except:
            pass
            
        # Barra di ricerca: tentiamo più XPath per robustezza
        search_box = None
        for xpath in [
            '//div[@contenteditable="true"][@data-tab="3"]',
            '//*[@id="side"]//div[@contenteditable="true"]',
            '//*[@id="side"]//p',
            '//*[@id="side"]//input',
            '//button[@aria-label="Cerca o inizia una nuova chat"]',
            '//div[@title="Cerca"]',
            '//div[@title="Cerca o inizia una nuova chat"]',
            '(//div[@contenteditable="true"])[1]'
        ]:
            try:
                # Aumentato il timeout a 8 secondi per ogni tentativo
                search_box = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, xpath)))
                break
            except:
                pass
                
        if not search_box:
            raise Exception("Impossibile trovare la barra di ricerca. WhatsApp Web potrebbe essere cambiato.")
            
        search_box.clear()
        search_box.send_keys(contact_name)
        time.sleep(3) # Pausa per permettere l'aggiornamento della lista
        
        if status_callback:
            status_callback(f"Selezionando il contatto: {contact_name}...")
            
        # Clicca sul contatto: tentiamo più XPath
        contact_el = None
        for xpath in [
            f'//span[@title="{contact_name}"]',
            f'//span[text()="{contact_name}"]',
            f'//div[@id="pane-side"]//span[contains(@title, "{contact_name}")]',
            f'//div[@id="pane-side"]//span[contains(text(), "{contact_name}")]'
        ]:
            try:
                contact_el = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                break
            except:
                pass
                
        if contact_el:
            contact_el.click()
        else:
            # FALLBACK POTENTE: Premiamo INVIO sulla barra di ricerca per aprire il primo risultato.
            # Questo funziona sempre, anche quando si inserisce un numero di telefono non salvato in rubrica.
            search_box.send_keys(Keys.ENTER)
            
        time.sleep(4) # Attendi il caricamento della chat
            
        if status_callback:
            status_callback("Scrittura del messaggio in corso...")
            
        # Barra del messaggio: div editabile nel footer
        message_box = None
        for xpath in [
            '//*[@id="main"]//footer//div[@contenteditable="true"]',
            '//div[@contenteditable="true"][@data-tab="10"]',
            '//*[@id="main"]//footer//p'
        ]:
            try:
                message_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
                break
            except:
                pass
                
        if not message_box:
            # Se la chat è chiusa o non si può scrivere (es. broadcast o contatto non valido)
            raise Exception("Impossibile trovare la barra dei messaggi. Forse la chat non si è aperta correttamente?")
            
        try:
            message_box.click()
        except:
            pass
        
        # Assicuriamoci che il messaggio sia una stringa valida per evitare errori
        safe_message = str(message) if message is not None else ""
        
        # Inviamo il testo riga per riga per gestire correttamente i ritorni a capo
        lines = safe_message.split('\n')
        for i, line in enumerate(lines):
            message_box.send_keys(line)
            if i < len(lines) - 1:
                message_box.send_keys(Keys.SHIFT, Keys.ENTER)
                
        # Invio finale tramite tasto ENTER (il metodo più veloce e infallibile su WhatsApp Web)
        try:
            message_box.send_keys(Keys.ENTER)
        except Exception as e:
            raise Exception(f"Errore durante l'invio finale del messaggio: {str(e)}")
        
        if status_callback:
            status_callback("Messaggio inviato correttamente!")
            
        # Attesa maggiore per assicurare che il messaggio venga spedito al server
        time.sleep(6)
        return {"success": True, "error": None}
        
    except Exception as e:
        if status_callback:
            status_callback("Errore! La finestra rimarrà aperta 20 secondi per farti vedere cos'è andato storto...")
        if driver:
            time.sleep(20) # Lascia il browser aperto per debugging visivo
        return {"success": False, "error": str(e)}
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
