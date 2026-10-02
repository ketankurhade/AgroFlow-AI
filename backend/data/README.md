# AgroFlow AI — Synthetic Historical Supply Chain Dataset

> **DISCLAIMER**: This dataset is synthetically generated for AgroFlow AI development and demonstration. It is not a representation of actual market, agricultural, weather, or spoilage statistics.

---

## 1. Dataset Purpose
This dataset provides 4,000 structured historical supply chain observations stored in the PostgreSQL table `historical_supply_chain_data`. It serves as the baseline dataset for future Machine Learning (ML) model training and experimentation in AgroFlow AI:
- **Part 4.4**: Demand Forecasting Model
- **Part 4.5**: Price Forecasting Model
- **Part 4.6**: ML Spoilage Prediction Model

---

## 2. Dataset Overview
- **Total Observations**: 4,000 rows
- **Date Range**: January 1, 2024 to September 28, 2026 (~2.7 years)
- **Random Seed**: `42` (Deterministic & Reproducible via `generate_historical_data.py`)
- **Database Table**: `historical_supply_chain_data`
- **Products Included (8)**:
  - Mango (*Category: Fruits*)
  - Tomato (*Category: Vegetables*)
  - Potato (*Category: Vegetables*)
  - Onion (*Category: Vegetables*)
  - Banana (*Category: Fruits*)
  - Grapes (*Category: Fruits*)
  - Apple (*Category: Fruits*)
  - Orange (*Category: Fruits*)

---

## 3. Schema & Column Specifications

### A. Meta & Feature Columns
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Unique observation record ID |
| `record_date` | Date (Indexed) | Observation date (`YYYY-MM-DD`) |
| `product_name` | String (Indexed) | Crop name (e.g., Mango, Tomato) |
| `category` | String (Indexed) | Produce category (Fruits, Vegetables) |
| `day_of_week` | Integer | Day index (0 = Monday, 6 = Sunday) |
| `month` | Integer | Calendar month (1 to 12) |
| `season` | String | Season (`Summer`, `Monsoon`, `Winter`, `Spring`) |
| `temperature` | Float | Storage/ambient temperature (°C) |
| `humidity` | Float | Relative humidity (%) |
| `inventory_age_days` | Integer | Days elapsed since harvest |
| `remaining_shelf_life_days` | Integer | Days remaining until estimated expiry |
| `inventory_quantity_kg` | Float | Stock level available in warehouse (kg) |
| `historical_demand_kg` | Float | Past/lagged demand feature (kg) |
| `supply_quantity_kg` | Float | Total market supply volume (kg) |

### B. Distinct Target Columns for Future ML
| Target Column | ML Task | Unit / Type | Description |
| :--- | :--- | :--- | :--- |
| `target_demand_quantity_kg` | **Demand Forecasting** | Float (kg) | Actual target demand quantity for the observation date. |
| `target_price_per_kg` | **Price Forecasting** | Float (₹/kg) | Wholesale market price per kg for the observation date. |
| `target_spoilage_indicator` | **Spoilage Classification** | Integer (`0` or `1`) | Binary indicator (1 = spoiled/high degradation, 0 = healthy). |

---

## 4. Synthetic Data Generation Logic & Relationships
1. **Demand Generation**: Derived from base product demand profiles scaled by seasonal demand multipliers (e.g. Mangoes peak in Summer, Apples in Winter), day-of-week retail spikes, and price elasticity, with additive Gaussian noise ($\sigma \approx 8\%$).
2. **Price Generation**: Derived from product base prices adjusted for supply vs. demand market ratio ($P \propto \frac{\text{Demand}}{\text{Supply}}$) with additive Gaussian noise.
3. **Spoilage Indicator Generation**: Evaluates a logistic probability function based on temperature excess above optimal, relative humidity, inventory harvest age, and remaining shelf life:
   $$z = -3.8 + 0.12(\text{Temp} - \text{OptTemp}) + 0.06(\text{Humidity} - 65) + 0.18(\text{Age} - 5) - 0.22(\text{ShelfLife})$$
   $$P(\text{Spoilage}) = \frac{1}{1 + e^{-z}}$$
   Observation is labeled `1` if $U(0,1) < P(\text{Spoilage})$, else `0`.

---

## 5. Prevention of Data Leakage
- Input features use **lagged/historical demand** (`historical_demand_kg`) rather than future demand.
- `target_demand_quantity_kg`, `target_price_per_kg`, and `target_spoilage_indicator` are stored in dedicated target columns and must **never** be passed as input features to training models.

---

## 6. Known Limitations
- Data is synthetic and generated for demonstration purposes.
- Environmental features (temperature and humidity) follow seasonal distributions rather than live meteorological APIs.
