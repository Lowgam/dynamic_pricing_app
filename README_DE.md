# Dynamic Pricing App – APricing

## 1. Projektübersicht

APricing ist eine Webanwendung, die im Rahmen des AP2-IHK-Projekts entwickelt wurde. Ziel des Projekts ist die intelligente und kontrollierte Preisgestaltung von Lebensmitteln, insbesondere von Produkten mit nahendem Mindesthaltbarkeitsdatum (MHD).

Das zentrale Problem besteht in der manuellen Preisverwaltung in Shopify: hoher Zeitaufwand, Fehleranfälligkeit und eingeschränkte Flexibilität bei der Preislogik. Bestehende Shopify-Apps erlauben keine ausreichende Kontrolle oder Nachvollziehbarkeit der Entscheidungslogik.

APricing löst dieses Problem durch ein **KI-unterstütztes Dynamic-Pricing-System**, bei dem Preisvorschläge durch eine künstliche Intelligenz berechnet, jedoch **ausschließlich nach manueller Freigabe durch den Benutzer angewendet** werden.

---

## 2. Projektziele

* Teilautomatisierung der Preisgestaltung
* Reduktion von Lebensmittelverschwendung
* Verbesserung von Abverkauf (Sell-Through) und Umsatz
* Sicherstellung von Kontrolle, Stabilität und Nachvollziehbarkeit

Eine automatische Preisänderung ohne Benutzerfreigabe ist technisch ausgeschlossen.

---

## 3. Systemarchitektur

### Technologiestack

* Backend: Python, FastAPI
* Datenbank: MySQL
* Frontend: HTML, Jinja2, Chart.js
* KI-Logik: Python (adaptive Gewichtung)

### Projektstruktur (vereinfacht)

```
dynamic_pricing_app/
├── app/
│   ├── routes/        # API- und UI-Endpunkte
│   ├── services/      # Geschäftslogik
│   ├── database/      # DB-Zugriff, Learning Store
│   ├── templates/     # HTML-Templates
│   └── static/        # JavaScript / CSS
├── logs/
├── scripts/
├── requirements.txt
└── README_*.md
```

---

## 4. End-to-End-Prozess

Der implementierte Prozess bildet einen vollständigen und konsistenten Datenfluss ab:

1. Import der Produkte aus Shopify (Mock oder real)
2. Anzeige der realen Produktdaten aus der Datenbank im Dashboard
3. Preissimulation durch den Pricing-Engine
4. Berechnung eines KI-Preisvorschlags (Korrekturkoeffizient)
5. Manuelle Bestätigung der Preisänderung durch den Benutzer
6. Speicherung eines Preisänderungsereignisses (`change_price_events`, Status OPEN)
7. Synchronisation dynamischer Daten (Verkäufe, Bestand, Velocity)
8. Abschluss des Ereignisses mit Ergebnisdaten (Status CLOSED)
9. Training der KI anhand abgeschlossener Ereignisse
10. Speicherung versionierter Gewichtungs-Snapshots
11. Verwendung der aktualisierten Gewichte für zukünftige Preisberechnungen

Damit wird ein geschlossener Lernkreislauf realisiert.

---

## 5. Pricing Engine

Der Pricing-Engine berechnet zunächst einen Basispreis unter Berücksichtigung folgender Faktoren:

* Restlaufzeit bis zum MHD
* Aktueller Lagerbestand
* Verkaufsgeschwindigkeit (Sales Velocity)
* Definierte Mindest- und Höchstgrenzen

Das Ergebnis ist der sogenannte **engined_price**, der als Grundlage für die KI-Anpassung dient.

---

## 6. KI-Engine – Adaptive Gewichtung

Die eingesetzte KI ist **keine Black Box**.

### Eingabewerte

* Lagerbestand
* Tage bis zum MHD
* Verkaufsvelocity
* Basispreis

### Ausgabewert

* Preis-Korrekturkoeffizient

### Begründung der Designentscheidung

Es wurde bewusst ein System mit **adaptiven Gewichten** gewählt, um:

* Transparenz der Entscheidungen sicherzustellen
* stabile Ergebnisse bei geringer Datenmenge zu gewährleisten
* jederzeitige Kontrolle und Rücksetzbarkeit zu ermöglichen

Der Einsatz komplexer Machine-Learning-Modelle ist erst vorgesehen, sobald eine statistisch relevante Datenbasis vorliegt.

---

## 7. KI-Trainer und Lernen

Der KI-Trainer:

* verarbeitet ausschließlich abgeschlossene (CLOSED) Preisänderungsereignisse
* vergleicht Verkaufsperformance vor und nach der Preisänderung
* berechnet relevante Kennzahlen (z. B. Sell-Through)
* aktualisiert die globalen KI-Gewichte
* speichert jede Änderung als versionierten Snapshot

Alle Snapshots sind einsehbar und können bei Bedarf zurückgesetzt werden (Rollback).

---

## 8. Kontrolle und Sicherheit

* Keine automatische Preisänderung ohne Benutzeraktion
* Durchsetzung von Preisgrenzen
* Vollständiges Logging aller Aktionen
* Versionierung und Rollback der KI-Gewichte
* Persistente Historie aller Preisentscheidungen

Das System ist darauf ausgelegt, unkontrollierte oder extreme Preisänderungen zu verhindern.

---

## 9. Projektstatus

Der Prototyp ist vollständig implementiert und funktionsfähig:

* Interaktives Dashboard
* KI-gestützte Preisvorschläge
* Aktiver Lernmechanismus
* Vollständig demonstrierbarer End-to-End-Prozess

Das Projekt ist bereit für die Präsentation im Rahmen der IHK-Abschlussprüfung.

---

## 10. Zukünftige Erweiterungen

* Anbindung an die reale Shopify-API
* Einsatz überwachter Machine-Learning-Modelle
* Einführung von Produktkategorien
* Einbindung externer Daten (Saisonalität, Wetter)
* Dockerisierung und CI/CD-Pipeline

---

## 11. Fazit

APricing zeigt, wie Dynamic Pricing mithilfe künstlicher Intelligenz praxisnah umgesetzt werden kann – kontrolliert, erklärbar und skalierbar. Der Mensch bleibt jederzeit Teil der Entscheidungsfindung.
