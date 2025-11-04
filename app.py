import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("📈 코스피200 주식 추천 시스템")
st.caption("초보자도 쉽게 이해하는 주식 분석 도구")

st.write("아래의 코스피200 주요 종목들을 간단한 기준으로 점수화하여 TOP 5를 추천합니다.")

# 一些示例 KOSPI200 成分股（雅虎财经代码）
TICKERS = {
    "삼성전자": "005930.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "현대자동차": "005380.KS",
    "삼성물산": "028260.KS",
    "LG화학": "051910.KS",
}

# 让用户选择分析多久的历史数据
days_back = st.slider("분석에 사용할 기간 (일)", 30, 180, 90)

end = datetime.today()
start = end - timedelta(days=days_back)

rows = []

st.sidebar.header("📊 점수 기준 (단순 예시)")
st.sidebar.write("- 1일 수익률이 양수이면 +3점")
st.sidebar.write("- 5일 이동평균이 20일 이동평균보다 높으면 +4점")

for name, code in TICKERS.items():
    try:
        hist = yf.download(code, start=start, end=end)
    except Exception:
        continue

    if hist.empty or len(hist) < 2:
        continue

    current_price = hist["Close"].iloc[-1]
    prev_price = hist["Close"].iloc[-2]
    change_pct = (current_price - prev_price) / prev_price * 100 if prev_price != 0 else 0

    ma5 = hist["Close"].tail(5).mean()
    ma20 = hist["Close"].tail(20).mean() if len(hist) >= 20 else hist["Close"].mean()

    # 简单打分逻辑
    score = 0
    if change_pct > 0:
        score += 3
    if ma5 > ma20:
        score += 4

    rows.append({
        "종목명": name,
        "티커": code,
        "현재가": round(float(current_price), 2),
        "1일 수익률(%)": round(float(change_pct), 2),
        "5일 이동평균": round(float(ma5), 2),
        "20일 이동평균": round(float(ma20), 2),
        "추천 점수": score,
    })

if not rows:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
else:
    df = pd.DataFrame(rows).sort_values("추천 점수", ascending=False)

    st.subheader("🎯 추천 종목 TOP 5")
    st.write("점수가 높을수록 최근 흐름이 양호한 종목입니다. (학습용 예시일 뿐, 실제 투자 추천이 아닙니다.)")

    top5 = df.head(5)

    # 用表格显示
    st.dataframe(top5.reset_index(drop=True))

    # 再用 metric 的形式逐个展示
    for _, row in top5.iterrows():
        st.markdown("---")
        st.subheader(f"{row['종목명']} ({row['티커']})")
        col1, col2, col3 = st.columns(3)
        col1.metric("현재가", f"{row['현재가']:.2f} 원")
        col2.metric("1일 수익률(%)", f"{row['1일 수익률(%)']:.2f} %")
        col3.metric("추천 점수", int(row["추천 점수"]))
