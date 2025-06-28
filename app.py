
import streamlit as st
import requests
from collections import Counter
import random

API_URL = "https://pcso-lotto-api.onrender.com/api/results/{}/stl-swer3"
DEFAULT_START_DATE = "2025-05-01"
MAX_ATTEMPTS_MULTIPLIER = 10

def fetch_history(start_date=DEFAULT_START_DATE):
    try:
        res = requests.get(API_URL.format(start_date))
        res.raise_for_status()
        return [entry["winningNumbers"] for entry in res.json()]
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

def analyze_frequencies(draws):
    positional = [Counter() for _ in range(3)]
    overall = Counter()
    for draw in draws:
        for i, digit in enumerate(draw):
            positional[i][digit] += 1
            overall[digit] += 1
    return positional, overall

def generate_predictions(freq_data, last_draw, count, sum_bounds, even_odd):
    top_digits = [[digit for digit, _ in freq_data[i].most_common(5)] for i in range(3)]
    predictions = []
    attempts = 0
    while len(predictions) < count and attempts < count * MAX_ATTEMPTS_MULTIPLIER:
        combo = [random.choice(top_digits[i]) for i in range(3)]
        if random.random() < 0.4:
            combo[random.randint(0, 2)] = last_draw[random.randint(0, 2)]
        combo_int = list(map(int, combo))
        total = sum(combo_int)
        evens = sum(1 for d in combo_int if d % 2 == 0)
        odds = 3 - evens
        if sum_bounds[0] <= total <= sum_bounds[1] and (evens, odds) == even_odd:
            predictions.append("".join(map(str, combo_int)))
        attempts += 1
    return predictions

st.set_page_config("Swertres Predictor", layout="centered")
st.title("Swertres Lotto Prediction")
st.markdown("Predict Swertres combinations using digit frequency analysis.")

num_predictions = st.slider("Number of Predictions", 1, 50, 10)
sum_min = st.slider("Minimum Digit Sum", 0, 27, 10)
sum_max = st.slider("Maximum Digit Sum", sum_min, 27, 27)
even_digits = st.slider("Even Digits Count", 0, 3, 1)
odd_digits = 3 - even_digits

if st.button("Generate"):
    results = fetch_history()
    if results:
        pos_freq, total_freq = analyze_frequencies(results)
        latest_draw = results[-1]
        preds = generate_predictions(
            pos_freq,
            latest_draw,
            count=num_predictions,
            sum_bounds=(sum_min, sum_max),
            even_odd=(even_digits, odd_digits)
        )

        st.success(f"Last Draw: {latest_draw}")
        st.subheader("Predictions")
        st.write(", ".join(preds))

        hot = ", ".join(d for d, _ in total_freq.most_common(3))
        cold = ", ".join(d for d, _ in total_freq.most_common()[-3:])

        st.subheader("Hot Numbers")
        st.write(hot)

        st.subheader("Cold Numbers")
        st.write(cold)
    else:
        st.warning("No history available to generate predictions.")
