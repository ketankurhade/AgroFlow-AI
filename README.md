# AgroFlow AI — Smart Agricultural Supply Chain Intelligence Platform

AgroFlow AI is an end-to-end intelligent agricultural supply chain management platform designed for cold-chain optimization, demand/price forecasting, spoilage prediction, and operational decision support.

---

## AgroFlow Intelligence Decision Layer (Part 4.7)

The **AgroFlow Intelligence Decision Layer** (`POST /api/intelligence/analyze`) is a lightweight orchestrator that synthesizes inputs from all active prediction and optimization modules into actionable operational recommendations.

### Architecture Overview

```text
                                +-----------------------------+
                                |  React Frontend Dashboard   |
                                +--------------+--------------+
                                               |
                                               v
                                +-----------------------------+
                                | POST /api/intelligence/     |
                                |         analyze             |
                                +--------------+--------------+
                                               |
                                               v
                                +-----------------------------+
                                |    Intelligence Service     |
                                +--+--------+--------+-----+--+
                                   |        |        |     |
      +----------------------------+        |        |     +---------------------------+
      |                                     |        |                                 |
      v                                     v        v                                 v
+-----------------------+ +--------------------+ +-------------------+ +-----------------------+
|  Demand Forecasting   | | Price Forecasting  | | Rule-Based        | | ML Spoilage           |
|  (RandomForest)       | | (RandomForest)     | | Spoilage Engine   | | Classifier            |
|  POST /demand/predict | | POST /price/predict| | GET /spoilage/risk| | POST /spoilage/ml-pred|
+-----------------------+ +--------------------+ +-------------------+ +-----------------------+
```

### Key Architectural Principles

1. **No Retraining or Duplicate Pipelines**: The decision layer calls existing service modules without retraining models or duplicating scikit-learn pipelines.
2. **Deterministic Operational Heuristics**: Decision rules evaluate transparent threshold conditions to output standardized priority levels (`CRITICAL`, `HIGH`, `NORMAL`, `MONITOR`).
3. **Strict Metric Separation**: Part 4.2 Rule-Based Risk Score (0-100) and Part 4.6 ML Spoilage Probability (0.0 - 1.0) are presented separately and are never averaged or combined into artificial scores.
4. **Synthetic Demonstration Disclaimer**: Demand, price, and spoilage ML models are trained on a 4,000-record synthetic demonstration dataset. Route optimization uses geographic Haversine distance calculations at an assumed 50 km/h average speed without live GPS/traffic feeds.
5. **Non-Guarantee Decision Support**: Operational recommendations are decision-support suggestions rather than guarantees or certified food-safety promises.

---

## Active API Endpoints

- `GET /api/health` — System health check
- `POST /api/auth/login` — Authentication token generation
- `POST /api/routes/optimize` — OR-Tools TSP route optimization
- `GET /api/spoilage/risk` — Rule-based spoilage heuristics
- `GET /api/spoilage/summary` — Aggregate spoilage metrics
- `POST /api/demand/predict` — ML demand forecasting
- `GET /api/demand/model-summary` — Demand model metrics
- `POST /api/price/predict` — ML price forecasting
- `GET /api/price/model-summary` — Price model metrics
- `POST /api/spoilage/ml-predict` — ML spoilage classification
- `GET /api/spoilage/ml-model-summary` — Spoilage model metrics
- `POST /api/intelligence/analyze` — **Part 4.7 Intelligence Integration & Operational Decision Layer**

---

## Verification & Testing

Run full backend test suite:

```bash
cd backend
python test_demand_model.py
python test_price_model.py
python test_spoilage_ml.py
python test_intelligence.py
python test_full_system.py
```

Run frontend production build:

```bash
cd frontend
npm run build
```
