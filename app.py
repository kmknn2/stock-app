import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 종목 이름 -> 코드 변환 사전
STOCK_DICT = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS",
    "기아": "000270.KS",
    "카카오": "035720.KS",
    "네이버": "035420.KS",
    "포스코홀딩스": "005490.KS",
    "LG화학": "051910.KS",
    "삼성SDI": "006400.KS",
    "KB금융": "105560.KS",
    "신한지주": "055550.KS",
    "하나금융지주": "086790.KS",
    "삼성물산": "028260.KS",
    "현대모비스": "012330.KS",
    "LG전자": "066570.KS",
    "SK텔레콤": "017670.KS",
    "KT": "030200.KS",
    "셀트리온": "068270.KS",
}

st.title("📈 주식 매수/매도 신호 앱")

# 종목 검색
search = st.text_input("종목 이름 검색 (예: 삼성전자, 카카오, 현대차)")

# 검색 결과 필터링
if search:
    results = {k: v for k, v in STOCK_DICT.items() if search in k}
    if results:
        selected = st.selectbox("종목 선택", list(results.keys()))
        ticker = results[selected]
        st.info(f"선택된 종목 코드: {ticker}")
    else:
        st.warning("검색 결과가 없어요. 다른 이름으로 검색해보세요.")
        ticker = None
else:
    ticker = None

period = st.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y"])
ma_short = st.slider("단기 이동평균 (MA)", min_value=3, max_value=20, value=5)
ma_long = st.slider("장기 이동평균 (MA)", min_value=10, max_value=60, value=20)

if st.button("조회하기 🔍"):
    if ticker is None:
        st.error("먼저 종목을 검색하고 선택해주세요.")
    else:
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
