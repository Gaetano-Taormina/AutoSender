# 🤖 AutoSender (for WhatsApp Web)

[![Standalone App](https://img.shields.io/badge/📦_Standalone_App-Ready-success?style=for-the-badge)](#-compilation-and-execution)

> **Nota Legale / Legal Note:** Questo è un progetto indipendente e non è affiliato, autorizzato, mantenuto, sponsorizzato o supportato in alcun modo da WhatsApp Inc. o Meta Platforms, Inc. "WhatsApp" è un marchio registrato dei rispettivi proprietari. L'utilizzo di questo nome avviene unicamente a scopo descrittivo (Nominative Fair Use) per indicare la compatibilità del software.

🌍 **Choose your language / Scegli la tua lingua:**

- [🇬🇧 English Version](#-english-version)
- [🇮🇹 Versione Italiana](#-versione-italiana)

---

## 🇬🇧 English Version

AutoSender is a modern, standalone desktop application that allows users to schedule and automate the sending of messages on WhatsApp Web. Designed with privacy and simplicity in mind, it operates entirely on your local machine without requiring external servers or complex installations.

### 🌟 Key Features

- **Message Scheduling & Repeats:** Schedule messages to be sent at specific dates and times, and configure repeating messages at customized intervals (seconds/minutes).
- **Smart Autocomplete:** The system automatically remembers previously used numbers or names and suggests them instantly via a native dropdown.
- **Pending Tasks Management:** Easily view, monitor, or delete scheduled messages before they are sent.
- **Background Autostart:** Seamlessly runs in the background. It automatically starts on Windows boot (via a hidden VBS script) to ensure your scheduled messages are sent even if you haven't opened the UI.
- **Standalone Executable:** Thanks to PyInstaller, the app is packaged into a single `.exe` file. Users can run the application with a double-click without needing to install Python, Node.js, or any other dependencies.
- **Ghost Mode (Minimized Execution):** The internal browser operates completely in the background or minimized. It will never abruptly pop up and interrupt your work. Uses `webdriver-manager` to automatically handle Edge drivers.
- **Modern UI:** A beautiful, responsive interface built with React, featuring a sleek Dark Mode, Glassmorphism effects, and Live Logs to monitor background activity.
- **100% Local Privacy:** All data (contacts and pending messages) are stored securely in local JSON files. No data is ever sent to third-party servers.

### ⚖️ Privacy & Legal Compliance (GDPR & EU AI Act)

This software has been strictly designed to comply with modern European data and technology regulations:

- **GDPR Compliance:** The application uses 100% local storage. It does not use cookies, trackers, or telemetrics. User data never leaves the local machine.
- **EU AI Act Compliance:** AutoSender is a deterministic Robotic Process Automation (RPA) tool. It does **NOT** utilize Artificial Intelligence (AI), Machine Learning (ML), or Automated Decision-Making (ADM) systems. It strictly executes explicit user commands without algorithmic deviation.
- **Fair Use & Anti-Spam:** This tool is intended for personal automation. Aggressive use or mass messaging (SPAM) violates WhatsApp's Terms of Service and may lead to a permanent ban of your phone number. **Use responsibly.**

### 🏗️ Architecture and Structure

The project features a hybrid Desktop architecture, combining the power of modern web technologies with native Python automation.

- **Frontend (UI):** Developed in React (via Vite) and styled with Bootstrap 5 for a fast and fluid experience. The build process removes hash cache-busting to maintain clean filenames (`index.js`, `index.css`).
- **Backend (Engine):** Powered by Python.
- **Bridge:** Uses **Eel** to create a seamless, bidirectional communication channel between the React frontend and the Python backend.
- **Automation:** Uses **Selenium** to interface with the web browser and automate the actual message-sending process.
- **Database:** A lightweight, invisible local storage system based on JSON files (`tasks.json` and `contacts.json`).

### 🔄 Data Flow & Automation

1. The user schedules a message via the React interface.
2. The data is sent to Python via Eel and saved in the local JSON database.
3. A background Python scheduler continuously checks the pending tasks.
4. When the exact time arrives, Python spawns a hidden or automated browser instance via Selenium, logs into WhatsApp Web (if a session exists), and dispatches the message.
5. The task is then removed from the pending queue.

### 🚀 Compilation and Execution

The application is designed to be fully portable for Windows users.
To build the standalone executable from the source code:

1. Install dependencies: `pnpm install`
2. Run the build script: `pnpm run build:exe`

This command compiles the React frontend and packages the Python engine (along with Selenium and Eel) into a single `AutoSender.exe` inside the `dist` folder.

---

## 🇮🇹 Versione Italiana

AutoSender è un'applicazione desktop moderna e indipendente che permette agli utenti di programmare e automatizzare l'invio di messaggi su WhatsApp Web. Progettata con un occhio di riguardo per la privacy e la semplicità, opera interamente sul computer locale senza richiedere server esterni o installazioni complesse.

### 🌟 Caratteristiche Principali

- **Programmazione e Ripetizione Messaggi:** Schedula i messaggi per l'invio in date e orari specifici e configura ripetizioni a intervalli personalizzati (secondi/minuti).
- **Completamento Automatico Intelligente:** Il sistema ricorda i numeri o nomi utilizzati in precedenza e li suggerisce istantaneamente tramite un menu a tendina nativo.
- **Gestione Code:** Visualizza, monitora o elimina facilmente i messaggi in sospeso prima che vengano inviati.
- **Avvio Automatico in Background:** Il motore di invio si avvia automaticamente all'accensione di Windows (tramite script VBS invisibile) per garantire che i messaggi vengano inviati all'orario stabilito senza dover aprire l'interfaccia.
- **Eseguibile Autonomo (Standalone):** Grazie a PyInstaller, l'app è impacchettata in un singolo file `.exe`. Gli utenti possono avviare l'applicazione con un doppio click senza dover installare Python, Node.js o altre dipendenze.
- **Modalità Fantasma (Esecuzione Minimizzata):** Il browser interno opera minimizzato in background per non interrompere il tuo lavoro. Sfrutta `webdriver-manager` per gestire in automatico i driver di Edge.
- **Interfaccia Moderna:** Un'interfaccia stupenda e reattiva creata con React, dotata di una sofisticata Dark Mode, effetti Glassmorphism e un visualizzatore di Log in tempo reale.
- **Privacy Locale al 100%:** Tutti i dati (contatti e messaggi in attesa) sono salvati in modo sicuro in file JSON locali. Nessun dato viene mai trasmesso a server di terze parti.

### ⚖️ Conformità Legale e Privacy (GDPR e AI Act)

Questo software è stato rigorosamente progettato per rispettare le moderne normative europee sui dati e sulle tecnologie:

- **Conformità GDPR:** L'applicazione utilizza un'archiviazione locale al 100%. Non fa uso di cookie, tracciatori o telemetria. I dati dell'utente non lasciano mai la macchina locale.
- **Conformità EU AI Act:** AutoSender è uno strumento di automazione dei processi robotici (RPA) di natura deterministica. **NON** utilizza Intelligenze Artificiali (IA), Machine Learning (ML) o sistemi decisionali automatizzati. Esegue rigorosamente e ciecamente i comandi espliciti dell'utente senza deviazioni algoritmiche.
- **Fair Use e Anti-Spam:** Questo strumento è concepito per l'automazione personale. L'invio massivo di messaggi a sconosciuti (SPAM) viola i Termini di Servizio di WhatsApp e può causare il ban permanente del tuo numero. **Usa con responsabilità.**

### 🏗️ Architettura e Struttura

Il progetto è basato su un'architettura Desktop ibrida, che unisce la potenza delle moderne tecnologie web con l'automazione nativa di Python.

- **Frontend (Interfaccia):** Sviluppato in React (tramite Vite) e stilizzato con Bootstrap 5 per un'esperienza rapida e fluida. Il processo di build è configurato per mantenere i nomi dei file puliti (`index.js`, `index.css`).
- **Backend (Motore):** Gestito da Python.
- **Ponte di Comunicazione:** Utilizza **Eel** per creare un canale di comunicazione bidirezionale continuo tra il frontend React e il backend Python.
- **Automazione:** Utilizza **Selenium** per interfacciarsi col browser web e automatizzare il processo di digitazione e invio dei messaggi.
- **Database:** Un sistema di archiviazione locale e invisibile basato su file JSON (`tasks.json` e `contacts.json`).

### 🔄 Flusso dei Dati e Automazione

1. L'utente programma un messaggio tramite l'interfaccia React.
2. I dati vengono inviati a Python tramite Eel e salvati nel database JSON locale.
3. Uno scheduler Python in background controlla costantemente le attività in sospeso.
4. Quando scatta l'ora esatta, Python avvia un'istanza automatizzata del browser tramite Selenium, si collega a WhatsApp Web e invia il messaggio.
5. L'attività completata viene quindi rimossa dalla coda.

### 🚀 Compilazione ed Esecuzione

L'applicazione è progettata per essere totalmente portatile per gli utenti Windows.
Per costruire l'eseguibile standalone partendo dal codice sorgente:

1. Installa le dipendenze: `pnpm install`
2. Lancia lo script di build: `pnpm run build:exe`

Questo comando compilerà il frontend React e impacchetterà il motore Python (insieme a Selenium ed Eel) all'interno di un unico file `AutoSender.exe` situato nella cartella `dist`.
