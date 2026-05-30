const contactInput = document.getElementById('contactName');
const messageInput = document.getElementById('messageText');
const dateInput = document.getElementById('delayDate');
const timeInput = document.getElementById('delayTime');
const startBtn = document.getElementById('startBtn');
const statusArea = document.getElementById('statusArea');
const timerDisplay = document.getElementById('timerDisplay');
const statusMessage = document.getElementById('statusMessage');

let timerInterval;

startBtn.addEventListener('click', () => {
    const contact = contactInput.value.trim();
    const message = messageInput.value.trim();
    const timeVal = timeInput.value;
    const dateVal = dateInput.value;

    if (!contact || !message || !timeVal) {
        alert("Per favore, compila tutti i campi obbligatori (Destinatario, Messaggio, Orario).");
        return;
    }

    // Costruisci la data e l'ora target
    let targetDate = new Date();
    if (dateVal) {
        const [year, month, day] = dateVal.split('-');
        targetDate.setFullYear(parseInt(year), parseInt(month) - 1, parseInt(day));
    }
    
    // timeVal è nel formato "HH:MM" o "HH:MM:SS"
    const [hours, minutes, seconds] = timeVal.split(':');
    targetDate.setHours(parseInt(hours), parseInt(minutes), seconds ? parseInt(seconds) : 0, 0);

    const now = new Date();
    let totalSeconds = Math.floor((targetDate.getTime() - now.getTime()) / 1000);

    if (totalSeconds < 0) {
        alert("L'orario selezionato è già passato! Inserisci un orario futuro.");
        return;
    }

    // Disabilita i controlli dell'interfaccia utente durante il conteggio
    startBtn.disabled = true;
    contactInput.disabled = true;
    messageInput.disabled = true;
    dateInput.disabled = true;
    timeInput.disabled = true;

    // Mostra l'area di stato e il timer
    statusArea.classList.remove('hidden');
    
    // Salva il task nel database in modo permanente sul disco rigido
    const timestamp = targetDate.getTime() / 1000;
    eel.schedule_task(contact, message, timestamp)((response) => {
        if (response && response.success) {
            statusMessage.textContent = "Automazione programmata. Chiusura in corso...";
            statusMessage.style.color = "#128C7E";
            timerDisplay.textContent = "--- / ---";
            
            // Dopo 2 secondi, chiudi completamente la finestra
            setTimeout(() => {
                window.close();
            }, 2000);
        } else {
            statusMessage.textContent = "Errore nel salvataggio: " + (response ? response.error : "Sconosciuto");
            statusMessage.style.color = "red";
        }
    });
});

// Funzione esposta a Python per inviare aggiornamenti live alla UI
eel.expose(update_ui_status);
function update_ui_status(msg) {
    statusMessage.textContent = msg;
}
