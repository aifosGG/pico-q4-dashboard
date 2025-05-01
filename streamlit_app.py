
import streamlit as st
import plotly.graph_objects as go
from fetch_utils import *
import os, requests

st.set_page_config(page_title="Q4 Peak Probability", layout="wide")
st.title("🪙 Probabilidade de Pico no 4º Tri 2025")

# ---------- 1. Coletar dados -----------------
fed_prob = fedwatch_probs()
if fed_prob is None:
    st.warning("⚠️  FedWatch offline – usando 0 %.")   # <-- executa antes do score
    fed_prob = 0.0

etf_df = btc_etf_flows()
if etf_df.empty:
    st.warning("⚠️  Dados de fluxo ETF indisponíveis.")
    etf_5d_sum = 0
else:
    etf_5d_sum = etf_df["Total"].sum()

dom_btc  = btc_dominance()
yield_2y = two_year_yield().value.iloc[-1] if not two_year_yield().empty else 3.0
nfci     = nfc_index().value.iloc[-1]       if not nfc_index().empty       else -0.25
# ---------- 2. Score sintético 0-100 ---------
def z(val, mean, std):
    return (val - mean) / std

score = (
    0.25 * (fed_prob / 100) +
    0.15 * (1 - z(yield_2y, 3.0, 0.5)) +
    0.15 * (1 - z(nfci, -0.25, 0.3)) +
    0.15 * (z(etf_5d_sum, 500, 500)) +
    0.10 * (1 - z(dom_btc, 50, 5)) +
    0.10 * (1 - z(20, 20, 5)) +
    0.10 * 0.5
)
score = max(0, min(1, score)) * 100

# ---------- 3. Gauge -------------------------
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score,
    title={"text": "Q4-Peak Score"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "royalblue"},
        "steps": [
            {"range": [0, 40], "color": "tomato"},
            {"range": [40, 70], "color": "gold"},
            {"range": [70, 100], "color": "lightgreen"},
        ],
    },
))
st.plotly_chart(fig, use_container_width=True)

# ---------- 4. Métricas rápidas --------------
col1, col2 = st.columns(2)
with col1:
    st.subheader("FedWatch – próxima reunião")
    st.metric(label="Prob. Corte (%)", value=f"{fed_prob:.1f}")
with col2:
    st.subheader("Fluxo ETFs BTC (5 dias, US$ mi)")
    st.metric(label="Entrada líquida", value=f"{etf_5d_sum:,.0f}")

st.divider()
st.write("Últimos 5 dias de fluxo por ETF")
st.dataframe(etf_df)

# ---------- 5. Alerta Telegram ----------------
token = os.getenv("TELEGRAM_TOKEN")
chat  = os.getenv("TELEGRAM_CHAT_ID")
if token and chat and (score < 40 or score > 70):
    text = f"🌡️ Q4-Peak Score agora: {score:.1f}"
    try:
        requests.get(
            f"https://api.telegram.org/bot{token}/sendMessage",
            params={"chat_id": chat, "text": text},
            timeout=10,
        )
    except Exception as e:
        st.warning(f"Falha ao enviar alerta Telegram: {e}")
