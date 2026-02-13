import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import joblib
import os
import warnings

warnings.filterwarnings("ignore")


def load_data(filepath):
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y")
    df = df.sort_values("Date").reset_index(drop=True)
    df = df.drop(columns=["Index Name"])
    return df


def add_features(df):
    """Add moving averages and other technical indicators as features."""
    df["MA_5"] = df["Close"].rolling(window=5).mean()
    df["MA_20"] = df["Close"].rolling(window=20).mean()
    df["MA_50"] = df["Close"].rolling(window=50).mean()

    # volatility (std dev over 10 days)
    df["volatility_10"] = df["Close"].rolling(window=10).std()

    # daily return percentage
    df["daily_return"] = df["Close"].pct_change() * 100

    # price range for the day
    df["day_range"] = df["High"] - df["Low"]

    df = df.dropna().reset_index(drop=True)
    return df


def prepare_prophet_data(df, target_col, regressor_cols):
    """Convert dataframe into Prophet's expected format."""
    prophet_df = df[["Date", target_col] + regressor_cols].copy()
    prophet_df = prophet_df.rename(columns={"Date": "ds", target_col: "y"})
    return prophet_df


def train_prophet_model(train_df, regressor_cols):
    """Train a Prophet model with given regressors."""
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.1,
        seasonality_prior_scale=10.0,
    )

    for col in regressor_cols:
        model.add_regressor(col)

    model.fit(train_df)
    return model


def evaluate_model(model, test_df, target_name):
    """Evaluate model on test data and print metrics."""
    forecast = model.predict(test_df)
    y_true = test_df["y"].values
    y_pred = forecast["yhat"].values

    mae = mean_absolute_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100

    print(f"  {target_name}:")
    print(f"    MAE  = {mae:.2f}")
    print(f"    MAPE = {mape:.2f}%")

    return mae, mape


def main():
    print("Loading data...")
    df = load_data("NIFTY 50_last 10yrs.csv")
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")

    print("\nAdding technical features...")
    df = add_features(df)

    # split into train and test (last 60 trading days as test)
    split_point = len(df) - 60
    train_df = df.iloc[:split_point].copy()
    test_df = df.iloc[split_point:].copy()
    print(f"Training samples: {len(train_df)}")
    print(f"Testing samples:  {len(test_df)}")

    # regressors that Prophet will use
    regressor_cols = ["MA_5", "MA_20", "MA_50", "volatility_10"]

    # targets we want to predict
    targets = ["Open", "High", "Low", "Close"]

    # create directory to save models
    os.makedirs("saved_models", exist_ok=True)

    print("\n--- Training Models ---\n")
    models = {}

    for target in targets:
        print(f"Training model for: {target}")

        train_prophet = prepare_prophet_data(train_df, target, regressor_cols)
        test_prophet = prepare_prophet_data(test_df, target, regressor_cols)

        model = train_prophet_model(train_prophet, regressor_cols)
        models[target] = model

        evaluate_model(model, test_prophet, target)

        # save the model
        model_path = f"saved_models/prophet_{target.lower()}.pkl"
        joblib.dump(model, model_path)
        print(f"  Saved to {model_path}\n")

    # also save the feature data (we need recent data for regressors)
    joblib.dump(df, "saved_models/processed_data.pkl")

    print("--- Training Complete ---")
    print("All models saved in saved_models/ directory.")


if __name__ == "__main__":
    main()
