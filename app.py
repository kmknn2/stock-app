import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 주식 매수/매도 신호 앱")

ticker = st.text_input("종목 코드 입력 (예: 005930.KS = 삼성전자)", value="005930.KS")
period = st.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y"])
ma_short = st.slider("단기 이동평균 (MA)", min_value=3, max_value=20, value=5)
ma_long = st.slider("장기 이동평균 (MA)", min_value=10, max_value=60, value=20)

if st.button("조회하기 🔍"):
    df = yf.download(ticker, period=period, auto_adjust=True)
    
    if df.empty:
        st.error("데이터를 불러올 수 없어요. 종목 코드를 확인해주세요.")
    else:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        
        df["MA_단기"] = df["Close"].rolling(ma_short).mean()
        df["MA_장기"] = df["Close"].rolling(ma_long).mean()
        df = df.dropna()

        last = df.iloc[-1]
        if last["MA_단기"] > last["MA_장기"]:
            st.success("🟢 현재 신호: 매수 구간")
        else:
            st.error("🔴 현재 신호: 매도 구간")

        buy = df[df["MA_단기"] > df["MA_장기"]]["Close"]
        sell = df[df["MA_단기"] < df["MA_장기"]]["Close"]

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(df.index, df["Close"], color="black", linewidth=1.5, label="Close")
        ax.plot(df.index, df["MA_단기"], color="blue", linestyle="--", label=f"MA{ma_short}")
        ax.plot(df.index, df["MA_장기"], color="orange", linestyle="--", label=f"MA{ma_long}")
        ax.scatter(buy.index, buy.values, color="red", marker="^", s=80, zorder=5, label="Buy")
        ax.scatter(sell.index, sell.values, color="blue", marker="v", s=80, zorder=5, label="Sell")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
