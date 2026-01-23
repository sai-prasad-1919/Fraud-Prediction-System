import pandas as pd

# load dataset once
data = pd.read_csv("data.csv")

def predict_risk(transaction_id):
    row = data[data["transaction_id"] == transaction_id]

    if row.empty:
        return "ID NOT FOUND"

    risk = row.iloc[0]["risk_level"]   # High / Medium / Low
    return risk
