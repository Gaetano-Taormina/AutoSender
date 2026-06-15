# WhatsApp Web Automator Bot (Local Privacy First)

A complete desktop application built with MVC architecture using Python (Eel) and Selenium. It allows you to schedule WhatsApp Web messages in a fully automated, secure, and local manner on your PC.

## 🌟 Key Features

- **Absolute Privacy**: It does not use external databases or cloud APIs. Everything runs locally on your computer, ensuring 100% privacy.

- **End-to-End Encryption (E2EE)**: Sensitive data (such as sessions or settings saved via cookies) are encrypted locally using the Web Crypto API (AES-GCM). Data saved in the browser is unreadable and secure without the need for external servers.

- **Dead Man's Switch / Scheduling**: You can schedule a message for a specific date and time. Perfect for emergency messages in case of unavailability.

- **Secure Session Maintenance**: It securely saves cookies and the session locally (`%LOCALAPPDATA%`), so you won't have to scan the QR code at every startup. The memory database does not conflict with OneDrive.

- **Robust Engine**: Contact search with multiple dynamic XPath selectors and intelligent fallbacks (automatic ENTER key) in case of missed selection (supports both exact names in the address book and direct phone numbers).

- **Network Block Bypass**: If you are behind corporate proxies or restrictive DNS, the architecture supports using an Edge driver downloaded manually in the root folder.

## 🛠️ Technologies Used

- **Backend/Controller**: Python 3 with `Eel`

- **Model/Automation**: `Selenium WebDriver` (Microsoft Edge)

- **Frontend**: HTML5, CSS3, Vanilla JavaScript (modern and elegant UI)

- **Security**: Web Crypto API (AES-GCM encryption for E2EE cookies)

## 🚀 Installation and Setup

1. **Clone the repository**:

   ```bash
   git clone <your_github_link>
   cd whatsapp_bot
   ```

2. **Install dependencies**:
   Make sure you have Python installed. Run:

   ```bash
   pip install -r assets/python/requirements.txt
   ```

3. **Download WebDriver (Optional, for networks with strict Firewalls)**:
   The bot will try to use the native Selenium Manager. If you get a network error, download the Microsoft Edge driver (same version as your browser) from [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) and extract the `msedgedriver.exe` file directly into this folder.

4. **Start the bot**:

   ```bash
   python main.py
   ```

## 💡 Usage Guide

1. **First start (Session Setup)**: Set a timer for a few seconds, write your number, and start the automation. Edge will open and you will need to **scan the QR Code**. This operation only needs to be done once.

2. **Normal Use**: Choose the recipient, write the message, set the date and time of sending, and click Start. The interface will count down, the program will wait for the set time, and do everything by itself!

## ⚠️ Warnings

The automation is based on the HTML structure (DOM) of WhatsApp Web. Since Meta frequently updates the layout, the code implements multiple "fallbacks" to find the buttons. Use this repository responsibly and in compliance with WhatsApp's Terms of Service.

---
---

## 🇮🇹 Versione Italiana: WhatsApp Web Automator Bot

Un'applicazione desktop completa, costruita con architettura MVC usando Python (Eel) e Selenium. Consente di schedulare l'invio di messaggi WhatsApp Web in modo totalmente automatizzato, sicuro e locale sul tuo PC.

## 🌟 Caratteristiche Principali

- **Privacy Assoluta**: Non usa database esterni né API cloud. Tutto gira in locale sul tuo computer garantendo il 100% della privacy.

- **Crittografia End-to-End (E2EE)**: I dati sensibili (come le sessioni o le impostazioni salvate tramite cookie) vengono crittografati localmente usando la Web Crypto API (AES-GCM). I dati salvati nel browser risultano illeggibili e sicuri senza bisogno di server esterni.

- **Dead Man's Switch / Schedulazione**: Puoi schedulare un messaggio per una data e un'ora precisa. Perfetto per messaggi di emergenza in caso di indisponibilità.

- **Mantenimento Sessione Sicuro**: Salva in modo sicuro i cookie e la sessione in locale (`%LOCALAPPDATA%`), così non dovrai scansionare il QR code ad ogni avvio. Il database di memoria non entra in conflitto con OneDrive.

- **Motore Robustissimo**: Ricerca del contatto con molteplici selettori XPath dinamici e fallback intelligenti (tasto INVIO automatico) in caso di mancata selezione (supporta sia nomi esatti in rubrica che numeri di telefono diretti).

- **Bypass Blocchi di Rete**: Se sei dietro proxy aziendali o DNS restrittivi, l'architettura supporta l'utilizzo di un driver Edge scaricato manualmente nella root.

## 🛠️ Tecnologie Utilizzate

- **Backend/Controller**: Python 3 con `Eel`

- **Model/Automazione**: `Selenium WebDriver` (Microsoft Edge)

- **Frontend**: HTML5, CSS3, Vanilla JavaScript (UI moderna ed elegante)

- **Sicurezza**: Web Crypto API (Crittografia AES-GCM per cookie E2EE)

## 🚀 Installazione e Avvio

1. **Clona la repository**:

   ```bash
   git clone <il_tuo_link_github>
   cd whatsapp_bot
   ```

2. **Installa le dipendenze**:
   Assicurati di avere Python installato. Esegui:

   ```bash
   pip install -r assets/python/requirements.txt
   ```

3. **Scarica il WebDriver (Opzionale, per reti con Firewall severi)**:
   Il bot proverà a usare il Selenium Manager nativo. Se ottieni un errore di rete, scarica il driver per Microsoft Edge (stessa versione del tuo browser) da [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) ed estrai il file `msedgedriver.exe` direttamente in questa cartella.

4. **Avvia il bot**:

   ```bash
   python main.py
   ```

## 💡 Guida all'uso

1. **Primo avvio (Setup Sessione)**: Imposta un timer di pochi secondi, scrivi il tuo numero e avvia l'automazione. Si aprirà Edge e dovrai **scansionare il QR Code**. Questa operazione va fatta una sola volta.

2. **Uso Normale**: Scegli il destinatario, scrivi il messaggio, imposta data e ora di invio e premi su Avvia. L'interfaccia farà il conto alla rovescia, il programma aspetterà l'orario stabilito e farà tutto da solo!

## ⚠️ Avvertenze

L'automazione si basa sulla struttura HTML (DOM) di WhatsApp Web. Poiché Meta aggiorna spesso il layout, il codice implementa molteplici "fallback" per trovare i bottoni. Usa questa repository in modo responsabile e nel rispetto dei Termini di Servizio di WhatsApp.
