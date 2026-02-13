from flask import Flask, render_template, request, flash, redirect, jsonify
from predict import predict_single_date, predict_for_dates
import joblib
import os

app = Flask(__name__)
app.secret_key = "nifty50-predictor"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    prediction_type = request.form.get("prediction_type")

    try:
        if prediction_type == "single":
            date_str = request.form.get("date")
            if not date_str:
                flash("Please select a date.")
                return redirect("/")
            result_df = predict_single_date(date_str)
        else:
            start = request.form.get("start_date")
            end = request.form.get("end_date")
            if not start or not end:
                flash("Please select both start and end dates.")
                return redirect("/")
            result_df = predict_for_dates(start, end)

        if result_df is None:
            flash("No trading days found in the selected range.")
            return redirect("/")

        predictions = result_df.to_dict(orient="records")
        return render_template("results.html", predictions=predictions)

    except Exception as e:
        flash(f"Something went wrong: {str(e)}")
        return redirect("/")


@app.route("/history")
def history():
    data = joblib.load(os.path.join(BASE_DIR, "saved_models", "processed_data.pkl"))
    # last 250 trading days (~1 year)
    recent = data.tail(250)[["Date", "Open", "High", "Low", "Close", "MA_5", "MA_20"]].copy()
    recent["Date"] = recent["Date"].dt.strftime("%d-%b-%Y")
    history_data = recent.to_dict(orient="records")

    # summary stats
    latest = data.iloc[-1]
    stats = {
        "latest_close": round(latest["Close"], 2),
        "latest_date": latest["Date"].strftime("%d-%b-%Y"),
        "year_high": round(data.tail(250)["High"].max(), 2),
        "year_low": round(data.tail(250)["Low"].min(), 2),
    }

    return render_template("history.html", history=history_data, stats=stats)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
