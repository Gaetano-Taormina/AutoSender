import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def init_driver(status_callback=None):
    """Initialize the webdriver using exclusively Microsoft Edge."""
    options = webdriver.EdgeOptions()
    # Invisible window (off-screen) but with desktop resolution to not break WhatsApp layout
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--window-position=0,0")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Find the REAL folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir)) # Go up from src/backend to main folder
    
    # Use AppData/Local for the profile to avoid OneDrive blocking database files (storage denied)
    local_appdata = os.environ.get('LOCALAPPDATA', root_dir)
    profile_dir = os.path.join(local_appdata, "AutoSender_Profile")
    options.add_argument(f"user-data-dir={profile_dir}")
    
    # Check if the user manually downloaded msedgedriver.exe in the executable folder
    driver_path = os.path.join(root_dir, 'msedgedriver.exe')
    
    if os.path.exists(driver_path):
        if status_callback: status_callback("Local driver found. Starting...")
        service = EdgeService(executable_path=driver_path)
        driver = webdriver.Edge(service=service, options=options)
    else:
        try:
            # Sopprimi i log fastidiosi di webdriver-manager
            import logging
            logging.getLogger('WDM').setLevel(logging.WARNING)
            os.environ['WDM_LOG_LEVEL'] = '0'
            os.environ['WDM_SSL_VERIFY'] = '0'
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
        except Exception as e2:
            raise Exception(f"Download 'msedgedriver.exe' and put it in the AutoSender folder. Error details: {str(e2)}")
        
    # Non minimizziamo più la finestra, perché Edge/Chrome sospendono l'esecuzione del Javascript (React)
    # quando la finestra è minimizzata, causando timeout sulla barra di ricerca nei messaggi successivi!
        
    return driver

def send_whatsapp_message(contact_name, message, status_callback=None, existing_driver=None, keep_open=False):
    """
    Core logic for sending the message on WhatsApp Web.
    status_callback is a function to update the UI.
    If existing_driver is provided, use that browser and do not close it.
    If keep_open is True, do not close the browser even if it was just opened.
    """
    driver = existing_driver
    try:
        if not driver:
            if status_callback:
                status_callback("Initializing browser...")
                
            driver = init_driver(status_callback)
            driver.get("https://web.whatsapp.com/")
            
            try:
                # Quick check if we are already logged in
                wait_fast = WebDriverWait(driver, 5)
                wait_fast.until(EC.presence_of_element_located((By.ID, "side")))
                if status_callback:
                    status_callback("Already connected! Initializing...")
            except TimeoutException:
                if status_callback:
                    status_callback("Waiting for WhatsApp Web (scan the QR code if requested)...")
                wait = WebDriverWait(driver, 120)
                wait.until(EC.presence_of_element_located((By.ID, "side")))
                if status_callback:
                    status_callback("Login confirmed. Initializing...")
                
            # Short pause to allow DOM stabilization after 'side' appears
            time.sleep(2)
        
        already_in_chat = False
        if existing_driver:
            if status_callback:
                status_callback(f"Using the open session for {contact_name}...")
            
            # Controllo magico: siamo GIÀ nella chat di questo contatto?
            try:
                # Usa XPath per prendere SOLO l'header della chat aperta (che si trova in id="main")
                header = driver.find_element(By.XPATH, '//*[@id="main"]//header')
                header_text = header.text.replace(" ", "").replace("-", "").replace("+", "").lower()
                normalized_contact = contact_name.replace(" ", "").replace("-", "").replace("+", "").lower()
                
                if normalized_contact and (normalized_contact in header_text or header_text in normalized_contact):
                    already_in_chat = True
                    if status_callback:
                        status_callback(f"Already inside the chat! Skipping search phase.")
            except:
                pass
                
            if not already_in_chat:
                # Se siamo in una chat diversa, premiamo ESC per uscire
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    for _ in range(3):
                        body.send_keys(Keys.ESCAPE)
                        time.sleep(0.3)
                except:
                    pass
        
        if not already_in_chat:
            # Search bar: try multiple XPaths for robustness
            search_box = None
            # Search bar: combined XPath for modern WhatsApp Web (IT/EN)
            search_xpath = (
                '//div[@title="Casella di testo per la ricerca"] | '
                '//div[@title="Search input textbox"] | '
                '//div[@contenteditable="true"][@data-tab="3"] | '
                '//*[@id="side"]//div[@contenteditable="true"] | '
                '//*[@id="side"]//p | '
                '//*[@id="side"]//input | '
                '//button[@aria-label="Cerca o inizia una nuova chat"] | '
                '//button[@aria-label="Search or start new chat"] | '
                '//div[@title="Cerca"] | '
                '//div[@title="Cerca o inizia una nuova chat"] | '
                '(//div[@contenteditable="true"])[1]'
            )
            try:
                # Timeout aumentato a 45 secondi
                search_box = WebDriverWait(driver, 45).until(EC.presence_of_element_located((By.XPATH, search_xpath)))
            except:
                search_box = None
                    
            if not search_box:
                raise Exception("Cannot find the search bar. WhatsApp Web might have changed.")
                
            # Clear the search bar
            try:
                search_box.send_keys(Keys.CONTROL + "a")
                search_box.send_keys(Keys.DELETE)
                time.sleep(0.5)
            except:
                pass
            search_box.clear()
            
            try:
                search_box.send_keys(contact_name)
            except:
                webdriver.ActionChains(driver).move_to_element(search_box).click().send_keys(contact_name).perform()
                
            if status_callback:
                status_callback(f"Selecting contact: {contact_name}...")
                
            # Search for contact name in the search results
            contact_xpath = (
                f'//span[@title="{contact_name}"] | '
                f'//span[text()="{contact_name}"] | '
                f'//div[@id="pane-side"]//span[contains(@title, "{contact_name}")] | '
                f'//div[@id="pane-side"]//span[contains(text(), "{contact_name}")]'
            )
            try:
                contact_el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, contact_xpath)))
            except:
                contact_el = None
                
            if contact_el:
                contact_el.click()
            else:
                # POWERFUL FALLBACK: Press ENTER on the search bar to open the first result.
                search_box.send_keys(Keys.ENTER)
            
            # Short pause to allow chat to open
            time.sleep(1)

            
        if status_callback:
            status_callback("Writing message...")
            
        # Message bar: combined XPath
        message_xpath = (
            '//*[@id="main"]//footer//div[@contenteditable="true"] | '
            '//*[@id="main"]//footer//p | '
            '//div[@title="Scrivi un messaggio"] | '
            '//div[@title="Type a message"]'
        )
        try:
            message_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, message_xpath)))
        except:
            message_box = None
                
        if not message_box:
            # If the chat is closed or cannot be written (e.g. broadcast or invalid contact)
            raise Exception("Cannot find the message bar. Maybe the chat didn't open correctly?")
            
        try:
            message_box.click()
        except:
            pass
        
        # Ensure the message is a valid string to avoid errors
        safe_message = str(message) if message is not None else ""
        

        # Import random here for anti-spam (now used only for small pauses)
        import random
        
        # Send text line by line (much faster)
        lines = safe_message.split('\n')
        for i, line in enumerate(lines):
            message_box.send_keys(line)
            if i < len(lines) - 1:
                message_box.send_keys(Keys.SHIFT, Keys.ENTER)
                time.sleep(0.05)
                
        # Final pause reduced to minimum
        time.sleep(random.uniform(0.1, 0.2))
        
        # Final send via ENTER key
        try:
            message_box.send_keys(Keys.ENTER)
        except Exception as e:
            raise Exception(f"Error during final message sending: {str(e)}")
        
        if status_callback:
            status_callback("Message sent successfully!")
            
        # Reduced wait after sending
        time.sleep(2)
        return {"success": True, "error": None, "driver": driver}
        
    except Exception as e:
        if status_callback:
            status_callback(f"Critical Error: {str(e)}")
            status_callback("The window will stay open for 20 seconds to show you what went wrong...")
        if driver and not existing_driver:
            time.sleep(20) # Leave the browser open for visual debugging
        return {"success": False, "error": str(e), "driver": driver}
        
    finally:
        if driver and not existing_driver and not keep_open:
            try:
                driver.quit()
            except:
                pass
