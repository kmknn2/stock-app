import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

st.title("📈 주식 매수/매도 신호 앱")

# 종목 입력
ticker = st.text_input("종목 코드 입력 (예: 005930.KS = 삼성전자)", value="005930.KS")

# 기간 선택
period = st.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y"])

# MA 설정
ma_short = st.slider("단기 이동평균 (MA)", min_value=3, max_value=20, value=5)
ma_long = st.slider("장기 이동평균 (MA)", min_value=10, max_value=60, value=20)

if st.button("조회하기 🔍"):
    df = yf.download(ticker, period=period, auto_adjust=True)
    df.columns = df.columns.droplevel(1)
    df["MA_단기"] = df["Close"].rolling(ma_short).mean()
    df["MA_장기"] = df["Close"].rolling(ma_long).mean()

    buy = df[df["MA_단기"] > df["MA_장기"]]["Close"]
    sell = df[df["MA_단기"] < df["MA_장기"]]["Close"]

    # 최근 신호
    last = df.iloc[-1]
    if last["MA_단기"] > last["MA_장기"]:
        st.success("🟢 현재 신호: 매수 구간")
    else:
        st.error("🔴 현재 신호: 매도 구간")

    # 그래프
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df.index, df["Close"], label="종가", color="black", linewidth=1.5)
    ax.plot(df.index, df["MA_단기"], label=f"MA{ma_short}", color="blue", linestyle="--")
    ax.plot(df.index, df["MA_장기"], label=f"MA{ma_long}", color="orange", linestyle="--")
    ax.scatter(buy.index, buy.values, color="red", marker="^", s=80, label="매수")
    ax.scatter(sell.index, sell.values, color="blue", marker="v", s=80, label="매도")
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
