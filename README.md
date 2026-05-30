# WhatsApp Web Automator Bot (Local Privacy First)

Un'applicazione desktop completa, costruita con architettura MVC usando Python (Eel) e Selenium. Consente di schedulare l'invio di messaggi WhatsApp Web in modo totalmente automatizzato, sicuro e locale sul tuo PC.

## 🌟 Caratteristiche Principali
- **Privacy Assoluta**: Non usa database esterni né API cloud. Tutto gira in locale sul tuo computer garantendo il 100% della privacy.
- **Dead Man's Switch / Schedulazione**: Puoi schedulare un messaggio per una data e un'ora precisa. Perfetto per messaggi di emergenza in caso di indisponibilità.
- **Mantenimento Sessione Sicuro**: Salva in modo sicuro i cookie e la sessione in locale (`%LOCALAPPDATA%`), così non dovrai scansionare il QR code ad ogni avvio. Il database di memoria non entra in conflitto con OneDrive.
- **Motore Robustissimo**: Ricerca del contatto con molteplici selettori XPath dinamici e fallback intelligenti (tasto INVIO automatico) in caso di mancata selezione (supporta sia nomi esatti in rubrica che numeri di telefono diretti).
- **Bypass Blocchi di Rete**: Se sei dietro proxy aziendali o DNS restrittivi, l'architettura supporta l'utilizzo di un driver Edge scaricato manualmente nella root.

## 🛠️ Tecnologie Utilizzate
- **Backend/Controller**: Python 3 con `Eel`
- **Model/Automazione**: `Selenium WebDriver` (Microsoft Edge)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (UI moderna ed elegante)

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
