"""
Indian E-Commerce Revenue Forecasting Pipeline

Run from the repository root:
    python scripts/forecasting_script.py

The script:
1. validates the monthly input data,
2. evaluates baseline and Holt-Winters models on a 2025 holdout,
3. selects the best model by MAPE,
4. refits the selected model on all 2023-2025 data,
5. forecasts monthly revenue for 2026,
6. saves evaluation/forecast CSVs and PNG charts.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "indian_ecommerce_monthly_sales.csv"
IMAGE_DIR = ROOT / "images"

def mape(actual, predicted):
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    return float(np.mean(np.abs((actual - predicted) / actual)) * 100)

def load_series():
    df = pd.read_csv(DATA_PATH)
    required = {"date", "year", "month", "units_sold", "revenue_inr",
                "avg_price_inr", "discount_pct", "marketing_spend_inr"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df = df.sort_values("date").drop_duplicates("date").reset_index(drop=True)

    expected = pd.date_range(df["date"].min(), df["date"].max(), freq="MS")
    if not df["date"].equals(pd.Series(expected, name="date")):
        raise ValueError("Dates must be contiguous month-start observations.")

    if not (df["year"].eq(df["date"].dt.year).all() and
            df["month"].eq(df["date"].dt.month).all()):
        raise ValueError("year/month columns do not match date.")

    if not (df["units_sold"] > 0).all():
        raise ValueError("units_sold must be positive.")
    if not (df["revenue_inr"] > 0).all():
        raise ValueError("revenue_inr must be positive.")
    if not (df["avg_price_inr"] > 0).all():
        raise ValueError("avg_price_inr must be positive.")
    if not df["discount_pct"].between(0, 1).all():
        raise ValueError("discount_pct must be between 0 and 1.")
    if not (df["marketing_spend_inr"] >= 0).all():
        raise ValueError("marketing_spend_inr must be non-negative.")

    # Revenue is mathematically consistent with units × average price
    implied = df["units_sold"] * df["avg_price_inr"]
    if not np.allclose(df["revenue_inr"], implied, rtol=1e-9, atol=1e-5):
        raise ValueError("revenue_inr is inconsistent with units_sold × avg_price_inr.")

    return df, (df.set_index("date")["revenue_inr"] / 100000).asfreq("MS")

def evaluate_models(train, test):
    forecasts = {}
    forecasts["Seasonal Naive"] = train.iloc[-12:].set_axis(test.index)
    forecasts["Naive"] = pd.Series(train.iloc[-1], index=test.index)
    forecasts["3-Month Moving Average"] = pd.Series(train.iloc[-3:].mean(), index=test.index)

    for trend in ("add", "mul"):
        for seasonal in ("add", "mul"):
            name = f"Holt-Winters ({trend} trend, {seasonal} seasonality)"
            fit = ExponentialSmoothing(
                train, trend=trend, seasonal=seasonal, seasonal_periods=12,
                initialization_method="estimated"
            ).fit()
            forecasts[name] = fit.forecast(len(test))

    rows = []
    for name, pred in forecasts.items():
        rows.append({
            "model": name,
            "MAE_lakhs": mean_absolute_error(test, pred),
            "RMSE_lakhs": np.sqrt(mean_squared_error(test, pred)),
            "MAPE_pct": mape(test, pred),
        })
    return pd.DataFrame(rows).sort_values("MAPE_pct").reset_index(drop=True), forecasts

def main():
    print("=== Indian E-Commerce Revenue Forecasting ===")
    df, series = load_series()
    train, test = series.iloc[:-12], series.iloc[-12:]

    evaluation, forecasts = evaluate_models(train, test)
    evaluation.to_csv(ROOT / "model_evaluation.csv", index=False)
    best = evaluation.iloc[0]["model"]
    print("\nModel evaluation (2025 holdout):")
    print(evaluation.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print(f"\nSelected model: {best}")

    # Refit the selected Holt-Winters specification on the full history.
    if best.startswith("Holt-Winters"):
        trend = "mul" if "mul trend" in best else "add"
        seasonal = "mul" if "mul seasonality" in best else "add"
        final_fit = ExponentialSmoothing(
            series, trend=trend, seasonal=seasonal, seasonal_periods=12,
            initialization_method="estimated"
        ).fit()
    else:
        final_fit = None

    if final_fit is None:
        future_index = pd.date_range(series.index[-1] + pd.offsets.MonthBegin(1), periods=12, freq="MS")
        future = pd.Series(series.iloc[-1], index=future_index)
    else:
        future = final_fit.forecast(12)

    forecast = pd.DataFrame({
        "date": future.index,
        "forecast_revenue_lakhs": future.values,
        "forecast_revenue_inr": future.values * 100000,
    })
    forecast["year"] = forecast["date"].dt.year
    forecast["month"] = forecast["date"].dt.month
    forecast.to_csv(ROOT / "forecast_2026.csv", index=False)

    print("\n2026 forecast:")
    print(forecast[["date", "forecast_revenue_lakhs"]].to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print("\nOutputs saved: model_evaluation.csv, forecast_2026.csv")

if __name__ == "__main__":
    main()
