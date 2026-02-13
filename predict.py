import pandas as pd
import numpy as np
import joblib
import os
import sys
import warnings

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_models():
    """Load all saved Prophet models and processed data."""
    targets = ["open", "high", "low", "close"]
    models = {}
    model_dir = os.path.join(BASE_DIR, "saved_models")
    for t in targets:
        models[t] = joblib.load(os.path.join(model_dir, f"prophet_{t}.pkl"))

    data = joblib.load(os.path.join(model_dir, "processed_data.pkl"))
    return models, data


def get_regressor_values(data, prediction_date):
    """
    Calculate regressor values for a future date.
    We use the most recent available data to compute moving averages
    and volatility, then carry them forward.
    """
    last_close = data["Close"].iloc[-1]
    ma_5 = data["Close"].iloc[-5:].mean()
    ma_20 = data["Close"].iloc[-20:].mean()
    ma_50 = data["Close"].iloc[-50:].mean()
    volatility_10 = data["Close"].iloc[-10:].std()

    return {
        "MA_5": ma_5,
        "MA_20": ma_20,
        "MA_50": ma_50,
        "volatility_10": volatility_10,
    }


def predict_for_dates(start_date, end_date):
    """Predict NIFTY 50 values for a date range."""
    models, data = load_models()

    # generate business days between start and end date
    dates = pd.bdate_range(start=start_date, end=end_date)

    if len(dates) == 0:
        print("No trading days in the given range.")
        return None

    # get regressor values from recent data
    regressors = get_regressor_values(data, dates[0])

    # build the future dataframe
    future_df = pd.DataFrame({"ds": dates})
    for col, val in regressors.items():
        future_df[col] = val

    # predict for each target
    results = {"Date": dates}
    for target_name, model in models.items():
        forecast = model.predict(future_df)
        results[target_name.capitalize()] = forecast["yhat"].values

    result_df = pd.DataFrame(results)
    result_df["Date"] = result_df["Date"].dt.strftime("%d-%b-%Y")

    return result_df


def predict_single_date(date_str):
    """Predict NIFTY 50 values for a single date."""
    return predict_for_dates(date_str, date_str)


def main():
    print("=" * 50)
    print("  NIFTY 50 Prediction System")
    print("=" * 50)

    while True:
        print("\nOptions:")
        print("  1. Predict for a single date")
        print("  2. Predict for a date range")
        print("  3. Exit")

        choice = input("\nEnter your choice (1/2/3): ").strip()

        if choice == "1":
            date_str = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                result = predict_single_date(date_str)
                if result is not None:
                    print("\nPredicted Values:")
                    print("-" * 60)
                    print(result.to_string(index=False))
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            start = input("Enter start date (YYYY-MM-DD): ").strip()
            end = input("Enter end date (YYYY-MM-DD): ").strip()
            try:
                result = predict_for_dates(start, end)
                if result is not None:
                    print(f"\nPredicted Values ({len(result)} trading days):")
                    print("-" * 60)
                    print(result.to_string(index=False))
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
