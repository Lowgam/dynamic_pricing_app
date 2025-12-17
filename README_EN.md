# Dynamic Pricing App – APricing

## 1. Introduction

APricing is a web application developed as part of the AP2 IHK project. It is designed to support intelligent price management for food products, with a specific focus on items approaching their expiration date.

The main problem addressed is the manual management of prices on Shopify: repetitive tasks, high risk of errors, and limited flexibility in pricing logic. Standard Shopify apps do not provide sufficient transparency or control over pricing algorithms.

APricing introduces an **AI-assisted dynamic pricing system**, where artificial intelligence generates price suggestions that **must always be approved by a human user**.

---

## 2. Project Goals

* Partially automate price management
* Reduce food waste
* Improve sell-through and revenue
* Ensure control, safety, and explainability

Prices are never changed automatically without user confirmation.

---

## 3. System Architecture

### Technology Stack

* Backend: Python, FastAPI
* Database: MySQL
* Frontend: HTML, Jinja2, Chart.js
* AI / Learning: custom Python logic with adaptive weights

### Project Structure (simplified)

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

## 4. End-to-End Workflow

1. Import products from Shopify (mock or real)
2. Display real products from the database in the dashboard
3. Simulate prices using the pricing_engine
4. Generate AI price suggestions (adjustment coefficient)
5. Manual confirmation of price changes by the user
6. Save a price change event in `change_price_events` (OPEN)
7. Synchronize dynamic data (sales, stock, velocity)
8. Close the event with outcome data (CLOSED)
9. AI Trainer updates the global weights
10. Save versioned snapshots with rollback capability
11. Updated weights are used for future price calculations

This workflow closes the learning loop.

---

## 5. Pricing Engine

The `pricing_engine` calculates a base price by considering:

* Days to expiration (MHD)
* Available stock
* Sales velocity
* Minimum and maximum safety thresholds

The output is an **engined_price**, which is then adjusted by the AI engine.

---

## 6. AI Engine – Adaptive Weights

The AI system is **not a black box**.

### Inputs

* stock
* days_to_expiry
* sales_velocity
* base price

### Output

* price adjustment coefficient

### Design Choice

An **adaptive weight system** was chosen to ensure:

* explainability
* stability
* full control over results

Advanced machine learning models will only be introduced once sufficient historical data is available.

---

## 7. AI Trainer

The AI Trainer:

* uses only CLOSED price change events
* compares before/after performance
* computes sell-through metrics
* updates global AI weights
* stores versioned snapshots

Each snapshot can be inspected and rolled back if necessary.

---

## 8. Control and Safety

* No automatic price updates
* Safety thresholds enforced
* Full logging of operations
* Weight snapshot rollback
* Persistent event history

The system is designed to prevent uncontrolled or extreme price changes.

---

## 9. Project Status

The prototype is complete and fully functional:

* Interactive dashboard
* AI-powered price suggestions
* Active learning mechanism
* Demonstrable end-to-end workflow

The project is ready for IHK presentation.

---

## 10. Future Improvements

* Real Shopify API integration
* Supervised machine learning models
* Product categories
* External data sources (seasonality, weather)
* Dockerization and CI/CD

---

## 11. Conclusion

APricing demonstrates how dynamic pricing can be implemented in a way that is intelligent, explainable, and controllable, while keeping humans in the decision loop.
