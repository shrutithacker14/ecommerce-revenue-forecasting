# 🇮🇳 Indian E-Commerce Revenue Forecasting

A portfolio-ready time-series forecasting project using **36 months of synthetic monthly Indian e-commerce data (Jan 2023–Dec 2025)**. The project evaluates simple baselines and Holt-Winters models, selects the best specification on a **2025 holdout**, and produces a 12-month **2026 revenue forecast**.

> **Important:** The dataset is synthetic/demo data. Forecasts are illustrative and should not be presented as real company or market forecasts.

## 🎯 Business Question

**How much monthly revenue should the business plan for in 2026, given trend and recurring seasonality?**

## 🔎 Approach

- Frequency: monthly (`MS`)
- History: Jan 2023–Dec 2025
- Holdout: Jan–Dec 2025
- Target: revenue in ₹ lakhs
- Baselines: Naive, Seasonal Naive, 3-month moving average
- Candidate models: Holt-Winters with additive/multiplicative trend and seasonality
- Model selection: lowest **MAPE** on the 2025 holdout
- Final forecast: selected model refit on all 36 months

## 📊 Model Evaluation

| Model | MAE (₹L) | RMSE (₹L) | MAPE |
|---|---:|---:|---:|
| Holt-Winters (add trend, mul seasonality) | 3.17 | 4.88 | 3.49% |\n| Holt-Winters (mul trend, mul seasonality) | 4.53 | 5.68 | 4.93% |\n| Holt-Winters (add trend, add seasonality) | 5.71 | 7.47 | 6.34% |\n| Holt-Winters (mul trend, add seasonality) | 8.24 | 8.76 | 10.10% |\n| Naive | 17.89 | 23.87 | 19.02% |\n| Seasonal Naive | 21.04 | 21.81 | 24.47% |\n| 3-Month Moving Average | 20.27 | 23.92 | 24.99% |\n
### Selected model

**Holt-Winters (add trend, mul seasonality)** is the best-performing specification on the 2025 holdout, with:

- **MAE:** ₹3.17 lakh
- **RMSE:** ₹4.88 lakh
- **MAPE:** 3.49%

The original project documentation reported different metrics because it described an **additive-seasonality** model. The audited version uses the objectively best holdout specification instead of hard-coding a model choice.

## 🔮 2026 Forecast

The final model forecasts approximately **₹1296.6 lakh (₹129.66 crore)** of revenue across 2026.

- Lowest forecast month: **February 2026 — ₹78.4 lakh**
- Peak forecast month: **November 2026 — ₹168.5 lakh**
- November vs January forecast: **110.4% higher**

These are **point forecasts**, not guaranteed outcomes. The dataset contains only three annual cycles, so uncertainty is meaningful and the model should be retrained as new monthly observations arrive.

## 💡 Business Interpretation

1. **Plan capacity around Q4.** October–December are consistently stronger in the historical series and remain the highest forecast period. Inventory and fulfillment planning should be completed before the festive peak.
2. **Use monthly forecasts for budgeting, not exact targets.** The model captures recurring seasonality but cannot anticipate promotions, competitor actions, macroeconomic shocks, or supply disruptions that are not represented in the data.
3. **Track forecast error monthly.** Once 2026 actuals arrive, compare them with the forecast and retrain/reselect the model rather than assuming the original model remains optimal.
4. **Do not infer causal ROI.** Marketing spend is included in the dataset, but this project does not estimate marketing elasticity or ROAS. A causal/regression analysis would be needed for that conclusion.

## 📸 Visuals

### Historical revenue
![Historical Revenue](images/01_historical_revenue_trend.png)

### Holdout performance
![Actual vs Forecast](images/02_model_forecast_comparison.png)

### 2026 forecast
![2026 Forecast](images/03_future_12_month_revenue_forecast.png)

## 📂 Repository Structure

```text
ecommerce_india_time_series_forecasting/
├── data/
│   └── indian_ecommerce_monthly_sales.csv
├── images/
│   ├── 01_historical_revenue_trend.png
│   ├── 02_model_forecast_comparison.png
│   └── 03_future_12_month_revenue_forecast.png
├── scripts/
│   └── forecasting_script.py
├── forecast_2026.csv
├── model_evaluation.csv
├── requirements.txt
├── .gitignore
└── README.md
```

## ▶️ Run Locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python scripts/forecasting_script.py
```

## 🧰 Skills Demonstrated

**Python · Pandas · NumPy · Statsmodels · Scikit-learn · Time-Series Forecasting · Model Evaluation · Data Validation · Business Interpretation · Data Visualization**

## ⚠️ Limitations

- Only 36 monthly observations are available.
- Only three seasonal cycles are observed.
- No external regressors (price, discount, marketing, holidays) are used in the forecast.
- No prediction intervals are presented; values are point forecasts.
- The data is synthetic and should not be interpreted as actual Indian e-commerce market data.
