# ---------------------- streamlit_app.py ----------------------
import streamlit as st
import plotly.graph_objects as go
from fetch_utils import *          # funções de APIs externas
import os, requests, pandas as pd

# -----------------------------------------------------------------
# 1. Configuração da página
# -----------------------------------------------------------------
st.set_page_config(page_title="Q4 Peak Probability", layout="wide")
st.title("🪙 Probabilidade de Pico no 4º Tri 2025")

# -----------------------------------------------------------------
# 2. Coleta de dados com tratamento de falhas
# -----------------------------------------------------------------
# FedWatch – probabilidade de corte
fed_prob = fedwatch_probs()
if fed_prob is None:
    st.warning("⚠️  FedWatch offline – usando 0 %.")
    fed_prob = 0.0

# Fluxo de ETFs de Bitcoin (5 dias)
etf_df = btc_etf_flows()
if etf_df.empty:
    st.warning("⚠️  Dados de fluxo ETF indisponíveis – usando 0.")
    etf_5d_sum = 0
else:
    etf_5d_sum = etf_df["Total"].sum()

# Dominância BTC (sempre numérico)
dom_btc = btc_dominance()
if dom_btc is None:
    st.warning("⚠️  CoinGecko offline – usando 50 % de dominância BTC.")
    dom_btc = 50.0
# Curva curta – rendimento Treasury 2-y
yield_df = two_year_yield()
yield_2y = yield_df.value.iloc[-1] if not yield_df.empty else 3.0   # fallback 3 %

# Condições financeiras – NFCI
nfci_df = nfc_index()
nfci = nfci_df.value.iloc[-1] if not nfci_df.empty else -0.25       # fallback -0,25

# -----------------------------------------------------------------
# 3. Cálculo do score 0-100
# -----------------------------------------------------------------
def z(val, mean, std):
    return (val - mean) / std

score = (
    0.25 * (fed_prob / 100) +
    0.15 * (1 - z(yield_2y, 3.0, 0.5)) +
    0.15 * (1 - z(nfci, -0.25, 0.3)) +
    0.15 * (z(etf_5d_sum, 500, 500)) +
    0.10 * (1 - z(dom_btc, 50, 5)) +
    0.10 * (1 - z(20, 20, 5)) +       # placeholder VIX
    0.10 * 0.5                        # placeholder EPS ex-Tech
)
score = max(0, min(1, score)) * 100

# -----------------------------------------------------------------
# 4. Interface
# -----------------------------------------------------------------
# Gauge
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

# Métricas rápidas
col1, col2 = st.columns(2)
with col1:
    st.subheader("FedWatch – próxima reunião")
    st.metric("Prob. Corte (%)", f"{fed_prob:.1f}")
with col2:
    st.subheader("Fluxo ETFs BTC (5 dias, US$ mi)")
    st.metric("Entrada líquida", f"{etf_5d_sum:,.0f}")

# Tabela de fluxos (se houver)
if not etf_df.empty:
    st.divider()
    st.write("Últimos 5 dias de fluxo por ETF")
    st.dataframe(etf_df)

# -----------------------------------------------------------------
# 5.
