import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
import time

# -------- CONFIG --------
st.set_page_config(page_title="CryptoTracker Pro", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for dark purple theme and fonts
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&family=Orbitron&display=swap');

html, body, [class*="css"]  {
    background: linear-gradient(135deg, #1e004d, #4b007d);
    color: #eee !important;
    font-family: 'Roboto Mono', monospace;
}

h1, h2, h3, h4, h5 {
    font-family: 'Orbitron', 'Roboto Mono', monospace !important;
    color: #d3b3ff !important;
}

.streamlit-expanderHeader {
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
}

.css-1d391kg {  /* sidebar color override */
    background-color: #2c005c !important;
}

.stButton>button {
    background: linear-gradient(45deg, #8a2be2, #4b0082);
    color: #eee;
    border-radius: 8px;
    font-weight: 600;
}

.stButton>button:hover {
    background: linear-gradient(45deg, #b266ff, #7d33ff);
    color: #fff;
}

.css-1v0mbdj {
    background: transparent !important;
}

a {
    color: #bb88ff;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
    color: #d3b3ff;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# -------- API Calls --------
COINGECKO_API = "https://api.coingecko.com/api/v3"
NEWS_API = "https://cryptocontrol.io/api/v1/public/news/coin/"  # Replace or mock if no key

# Get top 10 coins by market cap
@st.cache_data(ttl=600)
def get_top_coins():
    url = f"{COINGECKO_API}/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1, "sparkline": "false"}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        st.error("Failed to fetch coin data")
        return []

# Get historical price data for a coin
@st.cache_data(ttl=300)
def get_historical_data(coin_id, days=30):
    url = f"{COINGECKO_API}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        prices = data['prices']
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    else:
        st.error(f"Failed to fetch historical data for {coin_id}")
        return pd.DataFrame()

# Fetch crypto news for a coin (mocked if no API key)
def get_crypto_news(coin_symbol):
    # This is a placeholder. Replace with your own API and key.
    # Example: CryptoControl or NewsAPI integration here
    # return requests.get(f"{NEWS_API}{coin_symbol}").json()
    # Mock sample data:
    return [
        {"title": f"{coin_symbol} breaks new all-time high!", "url": "https://cryptonews.example.com/article1"},
        {"title": f"Experts discuss the future of {coin_symbol}", "url": "https://cryptonews.example.com/article2"},
        {"title": f"{coin_symbol} ecosystem updates and roadmap", "url": "https://cryptonews.example.com/article3"},
    ]

# -------- PLOTLY THEME --------
def plotly_dark_layout(title):
    return dict(
        template='plotly_dark',
        title=title,
        font=dict(family="Roboto Mono, monospace", size=14, color="#d3b3ff"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(115, 90, 255, 0.2)'),
        margin=dict(t=50, b=40, l=50, r=50),
    )

# -------- MAIN APP --------
def main():
    st.title("💜 CryptoTracker Pro")

    # Sidebar: Coin selector
    coins = get_top_coins()
    coin_names = [c['name'] for c in coins]
    coin_id_map = {c['name']: c['id'] for c in coins}
    coin_symbol_map = {c['name']: c['symbol'].upper() for c in coins}

    selected_coin = st.sidebar.selectbox("Select Cryptocurrency", coin_names, index=0)

    # Fetch historical price data
    with st.spinner(f"Fetching {selected_coin} data..."):
        df = get_historical_data(coin_id_map[selected_coin])

    # Plot price chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['price'], mode='lines+markers', line=dict(color="#b266ff", width=3), marker=dict(size=5)))
    fig.update_layout(plotly_dark_layout(f"{selected_coin} Price (Last 30 Days)"))

    # Two columns: Chart + News
    col1, col2 = st.columns([3, 1])

    with col1:
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"### 📰 Latest {selected_coin} News")
        news_items = get_crypto_news(coin_symbol_map[selected_coin])
        for news in news_items:
            st.markdown(f"- [{news['title']}]({news['url']})")

    # Footer
    st.markdown(
        """
        <div style="text-align:center; font-size:12px; margin-top:40px; color:#bb88ff;">
            Powered by <a href="https://www.coingecko.com/" target="_blank">CoinGecko API</a> and placeholder news.<br>
            Made with 💜 Streamlit & Plotly
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
