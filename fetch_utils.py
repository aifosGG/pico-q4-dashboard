
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
import json, requests

# --- FedWatch -------------------------------------------------
@st.cache_data(ttl=14400)  # guarda por 4 h
def fedwatch_probs():
    url = ("https://www.cmegroup.com/content/dam/cmegroup/"
           "fedwatch/target-rate-probabilities.json")
    for _ in range(3):
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            return float(r.json()["data"][0]["probabilityRateCut"])
        except Exception:
            time.sleep(2)
    return None

@st.cache_data(ttl=14400)
def btc_etf_flows():
    url = "https://farside.co.uk/cached_research/bitcoin_etf_flow.csv"
    for _ in range(3):
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            df = pd.read_csv(io.BytesIO(r.content))
            return df.tail(5)
        except Exception:
            time.sleep(2)
    return pd.DataFrame()  # vazio

@st.cache_data(ttl=3600)
def btc_dominance():
    url = "https://api.coingecko.com/api/v3/global"
    for _ in range(3):
        try:
            data = requests.get(url, timeout=30).json()
            return data["data"]["market_cap_percentage"]["btc"]
        except Exception:
            time.sleep(2)
    return None

def two_year_yield():
    return fred_series("DGS2").tail(30)

def nfc_index():
    return fred_series("NFCI").tail(12)
