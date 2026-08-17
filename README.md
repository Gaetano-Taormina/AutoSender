# 🤖 AutoSender (for WhatsApp Web)

[![Portable App](https://img.shields.io/badge/📦_Portable_App-Ready-success?style=for-the-badge)](#-compilation-and-execution)

> **Nota Legale / Legal Note:** Questo è un progetto indipendente e non è affiliato, autorizzato, mantenuto, sponsorizzato o supportato in alcun modo da WhatsApp Inc. o Meta Platforms, Inc. "WhatsApp" è un marchio registrato dei rispettivi proprietari. L'utilizzo di questo nome avviene unicamente a scopo descrittivo (Nominative Fair Use) per indicare la compatibilità del software.

🌍 **Choose your language / Scegli la tua lingua:**

- [🇬🇧 English Version](#-english-version)
- [🇮🇹 Versione Italiana](#-versione-italiana)

---

## 🇬🇧 English Version

AutoSender is a modern desktop application that allows users to schedule and automate the sending of messages on WhatsApp Web. Designed with privacy and simplicity in mind, it operates entirely on your local machine without requiring external servers.

### 🌟 Key Features

- **Message Scheduling & Repeats:** Schedule messages to be sent at specific dates and times, and configure repeating messages at customized intervals (seconds/minutes).
- **Smart Autocomplete:** The system automatically remembers previously used numbers or names and suggests them instantly via a native dropdown.
- **Pending Tasks Management:** Easily view, monitor, or delete scheduled messages before they are sent.
- **Background Autostart:** Seamlessly runs in the background. It automatically starts on Windows boot (via a hidden VBS script) to ensure your scheduled messages are sent even if you haven't opened the UI.
- **Portable Batch Launcher:** Uses a self-configuring batch file (`Avvia_AutoSender.bat`) that automatically provisions local virtual environments (Node and Python venv) without compiling heavy `.exe` files. This completely eliminates false-positive antivirus flags and prevents orphaned processes.
- **Ghost Mode (Minimized Execution):** The internal browser operates completely in the background. It uses `webdriver-manager` to automatically handle Edge drivers.
- **Modern UI:** A beautiful, responsive interface built with React, featuring a sleek Dark Mode, Glassmorphism effects, and Live Logs to monitor background activity.
- **100% Local Privacy:** All data (contacts and pending messages) are stored securely in local JSON files inside the `data/` project folder (USB-ready).

### ⚖️ Privacy & Legal Compliance (GDPR & EU AI Act)

This software has been strictly designed to comply with modern European data and technology regulations:

- **GDPR Compliance:** The application uses 100% local storage. It does not use cookies, trackers, or telemetrics. User data never leaves the local machine.
- **EU AI Act Compliance:** AutoSender is a deterministic Robotic Process Automation (RPA) tool. It does **NOT** utilize Artificial Intelligence (AI), Machine Learning (ML), or Automated Decision-Making (ADM) systems.
- **Fair Use & Anti-Spam:** This tool is intended for personal automation. Aggressive use or mass messaging (SPAM) violates WhatsApp's Terms of Service and may lead to a permanent ban of your phone number. **Use responsibly.**

### 🏗️ Architecture and Structure

The project features a hybrid Desktop architecture, combining modern web technologies with native Python automation, orchestrated by Node.js.

```text
📦 AutoSender
 ┣ 📂 src
 ┃ ┣ 📂 frontend           # React UI (Vite)
 ┃ ┗ 📂 backend            # Python Engine (Selenium, Scheduler, Eel)
 ┣ 📂 data                 # 100% Portable user database (JSON)
 ┣ 📂 release              # Output directory for clean portable launcher
 ┣ 📜 start.js             # Node.js Process Orchestrator
 ┣ 📜 Avvia_AutoSender.bat # Main automated entry point for users
 ┣ 📜 build_release.ps1    # PowerShell script to generate release folders
 ┗ 📜 package.json
```

- **Frontend (UI):** Developed in React (via Vite) and styled with Bootstrap 5.
- **Backend (Engine):** Powered by Python.
- **Bridge:** Uses **Eel** to create a seamless communication channel between React and Python.
- **Orchestrator:** A Node.js `start.js` script acts as a supervisor, ensuring that background Python processes are cleanly killed if the UI is closed (Process Monitor system).
- **Automation:** Uses **Selenium** to interface with the web browser.
- **Database:** Local storage based on JSON files (`tasks.json` and `contacts.json`) saved in the `data/` folder for complete USB portability.

### 🚀 Compilation and Execution

The application is designed to be fully portable for Windows users without needing `.exe` compilers like PyInstaller.

To run the application:
Simply double-click `Avvia_AutoSender.bat` inside the `release/` folder. It acts as an elegant lightweight shortcut that launches the app instantly from the root without duplicating environments.

---

## 🇮🇹 Versione Italiana

AutoSender è un'applicazione desktop moderna che permette agli utenti di programmare e automatizzare l'invio di messaggi su WhatsApp Web. Progettata con un occhio di riguardo per la privacy, opera interamente sul computer locale senza richiedere server esterni.

### 🌟 Caratteristiche Principali

- **Programmazione e Ripetizione Messaggi:** Schedula i messaggi per l'invio in date e orari specifici e configura ripetizioni a intervalli personalizzati.
- **Completamento Automatico Intelligente:** Il sistema ricorda i numeri utilizzati in precedenza e li suggerisce istantaneamente tramite un menu a tendina.
- **Gestione Code:** Visualizza, monitora o elimina facilmente i messaggi in sospeso.
- **Avvio Automatico in Background:** Il motore di invio si avvia automaticamente all'accensione di Windows (tramite script VBS invisibile).
- **Lanciatore Batch Portatile (No-EXE):** Sfrutta un file batch autoconfigurante (`Avvia_AutoSender.bat`) che gestisce autonomamente gli ambienti virtuali isolati (`.venv`). Questo elimina completamente i falsi positivi degli antivirus tipici dei file `.exe` e impedisce la creazione di "processi orfani".
- **Modalità Fantasma:** Il browser interno opera in background per non interrompere il tuo lavoro.
- **Interfaccia Moderna:** Un'interfaccia stupenda creata con React, dotata di Dark Mode, effetti Glassmorphism e Live Logs.
- **Privacy Locale al 100%:** Tutti i dati sono salvati in modo sicuro in file JSON locali nella cartella `data/` (USB-ready). Nessun dato viene mai trasmesso a server esterni.

### ⚖️ Conformità Legale e Privacy (GDPR e AI Act)

Questo software rispetta le moderne normative europee sui dati:

- **Conformità GDPR:** Archiviazione locale al 100%. Niente cookie o telemetria.
- **Conformità EU AI Act:** AutoSender è uno strumento di automazione RPA deterministica. **NON** utilizza Intelligenze Artificiali o Machine Learning.
- **Fair Use e Anti-Spam:** Concepito per l'automazione personale. L'invio massivo (SPAM) viola i Termini di WhatsApp e può causare il ban. **Usa con responsabilità.**

### 🏗️ Architettura e Struttura

Il progetto è basato su un'architettura ibrida supervisionata da Node.js.

```text
📦 AutoSender
 ┣ 📂 src
 ┃ ┣ 📂 frontend           # Interfaccia React (Vite)
 ┃ ┗ 📂 backend            # Motore Python (Selenium, Scheduler, Eel)
 ┣ 📂 data                 # Database utente 100% portatile su chiavetta
 ┣ 📂 release              # Cartella contenente il lanciatore pulito
 ┣ 📜 start.js             # Orchestratore Node.js
 ┣ 📜 Avvia_AutoSender.bat # Lanciatore automatico principale per l'utente
 ┣ 📜 build_release.ps1    # Script PowerShell per creare pacchetti di release
 ┗ 📜 package.json
```

- **Frontend (Interfaccia):** React (Vite) e Bootstrap 5.
- **Backend (Motore):** Python.
- **Ponte di Comunicazione:** **Eel** per collegare React a Python.
- **Orchestratore (Novità v1.1):** Uno script Node.js (`start.js`) fa da supervisore, garantendo che i processi Python vengano "uccisi" in modo pulito se l'interfaccia viene chiusa (Sistema di Monitoraggio Processi).
- **Automazione:** **Selenium** per la digitazione su WhatsApp Web.
- **Database:** File JSON locali salvati nella cartella `data/` del progetto per garantire totale Portabilità su chiavetta USB.

### 🚀 Compilazione ed Esecuzione

L'applicazione è progettata per essere totalmente portatile su Windows senza l'uso di instabili compilatori come PyInstaller.

Per avviare l'applicazione:
Fai doppio clic su `Avvia_AutoSender.bat` all'interno della cartella `release/AutoSender_v1.1`. Agirà come un telecomando leggero ed elegante per lanciare il bot senza dover duplicare file pesanti.
