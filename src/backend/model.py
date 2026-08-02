import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.service import Service as EdgeService

import sys
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import certifi

def init_driver(status_callback=None):
    """Initialize the webdriver using exclusively Microsoft Edge."""
    options = webdriver.EdgeOptions()
    # Invisible window (off-screen) but with desktop resolution to not break WhatsApp layout
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--window-position=0,0")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Find the REAL folder where AutoSender.exe is located
    if getattr(sys, 'frozen', False):
        root_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir)) # Go up from assets/python to main folder
    
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
            if status_callback: status_callback("Attempting to start default driver...")
            # Fallback to Selenium Manager if the file is missing (may give error in background)
            driver = webdriver.Edge(options=options)
        except Exception as e:
            if status_callback: status_callback("Base driver error. Downloading Edge driver (first time)...")
            # Configure SSL certificates for PyInstaller environment before downloading
            os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
            os.environ['SSL_CERT_FILE'] = certifi.where()
            os.environ['WDM_SSL_VERIFY'] = '1'
            
            try:
                service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
            except Exception as e2:
                raise Exception(f"Download 'msedgedriver.exe' and put it in the AutoSender.exe folder. Error details: {str(e2)}")
        
    # Minimize the window in the background as soon as it opens
    try:
        driver.minimize_window()
    except:
        pass
        
    return driver

def send_whatsapp_message(contact_name, message, status_callback=None, existing_driver=None):
    """
    Core logic for sending the message on WhatsApp Web.
    status_callback is a function to update the UI.
    If existing_driver is provided, use that browser and do not close it.
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
        else:
            if status_callback:
                status_callback(f"Using the open session to prepare the message for {contact_name}...")
        
        # Press ESCAPE on the page to automatically close any annoying popups, widgets or notifications
        try:
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            # Press ESCAPE again (closes previous chat or deselects search_box)
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
        except:
            pass
            
        # Search bar: try multiple XPaths for robustness
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
                # Increased timeout to 8 seconds for each attempt
                search_box = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, xpath)))
                break
            except:
                pass
                
        if not search_box:
            raise Exception("Cannot find the search bar. WhatsApp Web might have changed.")
            
        # Clear the search bar (if reusing the driver, there might be old text)
        try:
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)
            time.sleep(0.5)
        except:
            pass
        search_box.clear()
        
        search_box.send_keys(contact_name)
        # Removed fixed pause, rely on waiting for contact
        
        if status_callback:
            status_callback(f"Selecting contact: {contact_name}...")
            
        # Click on contact: try multiple XPaths
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
            # POWERFUL FALLBACK: Press ENTER on the search bar to open the first result.
            # This always works, even when entering a phone number not saved in contacts.
            search_box.send_keys(Keys.ENTER)
            
        # No fixed pause, wait directly for the message bar
            
        if status_callback:
            status_callback("Writing message...")
            
        # Message bar: editable div in the footer
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
            status_callback("Error! The window will stay open for 20 seconds to show you what went wrong...")
        if driver and not existing_driver:
            time.sleep(20) # Leave the browser open for visual debugging
        return {"success": False, "error": str(e), "driver": driver}
        
    finally:
        if driver and not existing_driver:
            try:
                driver.quit()
            except:
                pass
