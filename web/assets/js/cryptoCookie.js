// cryptoCookie.js
// Gestione dei cookie crittografati End-to-End

class CryptoCookieManager {
    constructor() {
        // Chiave univoca salvata localmente nel dispositivo (non viaggia mai in rete)
        this.keyName = "e2e_device_key";
        this.key = null;
    }

    async init() {
        let storedKey = localStorage.getItem(this.keyName);
        if (storedKey) {
            // Ripristina la chiave dal localStorage
            const keyBuffer = this.base64ToArrayBuffer(storedKey);
            this.key = await window.crypto.subtle.importKey(
                "raw",
                keyBuffer,
                "AES-GCM",
                true,
                ["encrypt", "decrypt"]
            );
        } else {
            // Crea una nuova chiave di sicurezza AES-256
            this.key = await window.crypto.subtle.generateKey(
                { name: "AES-GCM", length: 256 },
                true,
                ["encrypt", "decrypt"]
            );
            const exported = await window.crypto.subtle.exportKey("raw", this.key);
            localStorage.setItem(this.keyName, this.arrayBufferToBase64(exported));
        }
    }

    // Salva un cookie crittografato
    async setCookie(name, value, days = 7) {
        if (!this.key) await this.init();

        const encoder = new TextEncoder();
        const data = encoder.encode(value);
        
        // Vettore di inizializzazione casuale per la massima sicurezza
        const iv = window.crypto.getRandomValues(new Uint8Array(12));

        // Crittografia dei dati
        const encryptedData = await window.crypto.subtle.encrypt(
            { name: "AES-GCM", iv: iv },
            this.key,
            data
        );

        // Combina iv e dati in un'unica stringa
        const combined = new Uint8Array(iv.length + encryptedData.byteLength);
        combined.set(iv, 0);
        combined.set(new Uint8Array(encryptedData), iv.length);

        const base64Value = this.arrayBufferToBase64(combined.buffer);
        
        let expires = "";
        if (days) {
            let date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        
        // Crea il cookie (anche se rubato, sarà impossibile da leggere)
        document.cookie = name + "=" + encodeURIComponent(base64Value) + expires + "; path=/";
    }

    // Legge e decrittografa un cookie
    async getCookie(name) {
        if (!this.key) await this.init();

        let nameEQ = name + "=";
        let ca = document.cookie.split(';');
        let base64Value = null;
        
        for(let i=0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) == 0) base64Value = decodeURIComponent(c.substring(nameEQ.length,c.length));
        }

        if (!base64Value) return null;

        try {
            const combinedBuffer = this.base64ToArrayBuffer(base64Value);
            const iv = new Uint8Array(combinedBuffer.slice(0, 12));
            const encryptedData = combinedBuffer.slice(12);

            // Decrittografia
            const decryptedData = await window.crypto.subtle.decrypt(
                { name: "AES-GCM", iv: iv },
                this.key,
                encryptedData
            );

            const decoder = new TextDecoder();
            return decoder.decode(decryptedData);
        } catch (e) {
            console.error("Impossibile decrittografare il cookie. Dati corrotti o manipolati.", e);
            return null;
        }
    }

    // Helper conversioni
    arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    }

    base64ToArrayBuffer(base64) {
        let binary_string = window.atob(base64);
        let len = binary_string.length;
        let bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binary_string.charCodeAt(i);
        }
        return bytes.buffer;
    }
}

// Inizializza il modulo e lo rende disponibile
const secureCookies = new CryptoCookieManager();
secureCookies.init();
