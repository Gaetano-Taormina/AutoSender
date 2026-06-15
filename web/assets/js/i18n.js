// i18n.js
// Sistema di traduzione per l'interfaccia utente

const translations = {
    en: {
        app_title: "WhatsApp Auto Sender",
        app_subtitle: "Schedule your messages",
        label_contact: "Recipient (Exact name in contacts)",
        placeholder_contact: "E.g. John Doe",
        label_message: "Message",
        placeholder_message: "Write your message here...",
        label_when: "When to send the message?",
        title_date: "If omitted, uses today's date",
        title_time: "Format Hour:Minutes:Seconds",
        help_date: "The date is optional (defaults to today).",
        btn_start: "Start Automation",
        status_waiting: "Waiting..."
    },
    it: {
        app_title: "WhatsApp Auto Sender",
        app_subtitle: "Pianifica l'invio dei tuoi messaggi",
        label_contact: "Destinatario (Nome esatto in rubrica)",
        placeholder_contact: "Es. Mario Rossi",
        label_message: "Messaggio",
        placeholder_message: "Scrivi qui il tuo messaggio...",
        label_when: "Quando inviare il messaggio?",
        title_date: "Se omesso, usa la data di oggi",
        title_time: "Formato Ora:Minuti:Secondi",
        help_date: "La data è opzionale (di default è oggi).",
        btn_start: "Avvia Automazione",
        status_waiting: "In attesa..."
    }
};

function applyTranslations() {
    // Rileva la lingua del browser dell'utente
    const userLang = navigator.language || navigator.userLanguage; 
    
    // Seleziona 'it' se il browser è in italiano, altrimenti usa 'en' di default
    const lang = userLang.startsWith('it') ? 'it' : 'en';

    // Traduce il testo interno dei tag (es. h1, p, label, button)
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });

    // Traduce gli attributi 'placeholder' (es. per input e textarea)
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[lang][key]) {
            element.setAttribute('placeholder', translations[lang][key]);
        }
    });

    // Traduce gli attributi 'title' (es. per hover tooltip su input date/time)
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        if (translations[lang][key]) {
            element.setAttribute('title', translations[lang][key]);
        }
    });
}

// Applica le traduzioni non appena il DOM è caricato
document.addEventListener('DOMContentLoaded', applyTranslations);
