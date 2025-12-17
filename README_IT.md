# Dynamic Pricing App – APricing

## 1. Introduzione

APricing è una web application sviluppata come progetto AP2 IHK, progettata per supportare la gestione intelligente dei prezzi di prodotti alimentari, in particolare quelli prossimi alla scadenza.

Il problema principale è la gestione manuale dei prezzi su Shopify: operazioni ripetitive, alto rischio di errore e mancanza di flessibilità nelle logiche decisionali. Le soluzioni standard non permettono sufficiente controllo né spiegabilità degli algoritmi.

APricing introduce un sistema di **dynamic pricing assistito da IA**, in cui l’intelligenza artificiale genera suggerimenti di prezzo che **devono sempre essere approvati dall’utente**.

---

## 2. Obiettivo del progetto

* Automatizzare parzialmente la gestione dei prezzi
* Ridurre sprechi di prodotti in scadenza
* Migliorare sell-through e fatturato
* Garantire controllo, sicurezza e spiegabilità

Il sistema non applica mai modifiche di prezzo in modo autonomo.

---

## 3. Architettura generale

### Stack tecnologico

* Backend: Python, FastAPI
* Database: MySQL
* Frontend: HTML, Jinja2, Chart.js
* IA / Apprendimento: logica custom basata su pesi adattivi

### Struttura del progetto (semplificata)

```
dynamic_pricing_app/
├── app/
│   ├── routes/
│   ├── services/
│   ├── database/
│   ├── templates/
│   └── static/
├── logs/
├── scripts/
├── requirements.txt
└── README.md
```

---

## 4. Flusso End-to-End

1. Import prodotti da Shopify (mock o reale)
2. Visualizzazione prodotti reali in dashboard
3. Simulazione prezzi tramite pricing_engine
4. Calcolo suggerimento IA (coefficiente)
5. Conferma manuale del cambio prezzo
6. Salvataggio evento in change_price_events (OPEN)
7. Sincronizzazione dati dinamici
8. Chiusura evento con outcome (CLOSED)
9. AI Trainer aggiorna i pesi
10. Salvataggio snapshot e possibilità di rollback
11. Nuovi pesi utilizzati nei calcoli successivi

---

## 5. Motore di pricing

Il pricing_engine calcola un prezzo di base considerando:

* giorni alla scadenza (MHD)
* stock disponibile
* velocità di vendita
* soglie di sicurezza min/max

Il risultato è un **engined_price**, base per l’intervento dell’IA.

---

## 6. AI Engine – Pesi adattivi

L’IA non è una black box.

### Input

* stock
* days_to_expiry
* sales_velocity
* prezzo base

### Output

* coefficiente di aggiustamento applicato al prezzo

### Scelta progettuale

È stato scelto un sistema a **pesi adattivi** per garantire:

* spiegabilità
* stabilità
* controllo

Il Machine Learning avanzato verrà introdotto solo quando lo storico dati sarà statisticamente significativo.

---

## 7. AI Trainer

L’AI Trainer:

* utilizza solo eventi CLOSED
* confronta performance prima/dopo il cambio prezzo
* calcola metriche di sell-through
* aggiorna i pesi globali
* salva snapshot versionati

Ogni snapshot è ispezionabile e reversibile.

---

## 8. Sicurezza e controllo

* Nessun aggiornamento automatico dei prezzi
* Soglie di protezione
* Logging completo
* Rollback dei pesi
* Storico eventi persistente

---

## 9. Stato del progetto

Il prototipo è completo e funzionante:

* Dashboard interattiva
* Suggerimenti IA operativi
* Apprendimento attivo
* Flusso end-to-end dimostrabile

---

## 10. Sviluppi futuri

* Connessione Shopify reale
* IA avanzata supervisionata
* Categorie prodotto
* Dati esterni (stagione, meteo)
* Docker e CI/CD

---

## 11. Conclusione

APricing dimostra come il dynamic pricing possa essere implementato in modo intelligente, controllabile e spiegabile, mantenendo sempre l’essere umano al centro della decisione.
