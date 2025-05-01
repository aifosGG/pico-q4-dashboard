
import pandas as pd, requests, io, os

# ----------- FRED helper -----------------
FRED_KEY = os.getenv("FRED_KEY", "")
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

def fred_series(series_id):
    url = f"{FRED_URL}?series_id={series_id}&api_key={FRED_KEY}&file_type=json"
    data = requests.get(url, timeout=15).json()["observations"]
    return (
        pd.DataFrame(data)[["date", "value"]]
        .assign(value=lambda d: pd.to_numeric(d.value, errors='coerce'))
    )

# ----------- Funções de coleta -----------
def fedwatch_probs():
    url = "https://www.cmegroup.com/content/dam/cmegroup/fedwatch/target-rate-probabilities.json"
    data = requests.get(url, timeout=15).json()
    return float(data["data"][0]["probabilityRateCut"])

def btc_etf_flows():
    url = "https://farside.co.uk/cached_research/bitcoin_etf_flow.csv"
    csv = requests.get(url, timeout=15).content
    df = pd.read_csv(io.BytesIO(csv))
    return df.tail(5)

def btc_dominance():
    url = "https://api.coingecko.com/api/v3/global"
    return requests.get(url, timeout=15).json()["data"]["market_cap_percentage"]["btc"]

def two_year_yield():
    return fred_series("DGS2").tail(30)

def nfc_index():
    return fred_series("NFCI").tail(12)
