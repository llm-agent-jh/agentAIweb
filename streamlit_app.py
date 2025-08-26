import streamlit as st
import pandas as pd

# 📌 기본 설정
st.set_page_config(page_title="LLM Answer Viewer", layout="wide")

st.title("📄 LLM 응답 비교 Viewer")

# 📁 파일 경로
FILE_PATH = "RAG_final_v1_extracted_with_query_GT_qwen - RAG_final_v1_extracted_with_query.xlsx"  # ← 확장자에 맞춰 수정

# 📥 데이터 로드
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    # 엑셀/CSV 자동 처리
    if path.lower().endswith(".xlsx"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    return df

try:
    df = load_data(FILE_PATH)
except Exception as e:
    st.error(f"❌ 파일을 불러올 수 없습니다: {e}")
    st.stop()

# ==== 공통 유틸 ====
OUT_PHRASE = "우리가 가지고 있는 모델에서는 너의 요청을 해결해줄 수 없어."

def safe_contains(series: pd.Series, phrase: str) -> pd.Series:
    return series.astype(str).str.replace(r"\s+", " ", regex=True).str.strip().str.contains(phrase, na=False)

# 컬럼 존재 체크 (엑셀 헤더와 일치해야 함)
required_cols = ["Model Unique Name", "Query_korea", "GT", "qwen3 Answer", "gpt4o Answer"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"❌ 아래 컬럼이 파일에 없습니다: {missing}")
    st.stop()

# Out-of-Model 플래그 생성 (GT / qwen3 / gpt4o 중 하나라도 해당 문구면 True)
df["_out_gt"] = safe_contains(df["GT"], OUT_PHRASE)
df["_out_qwen"] = safe_contains(df["qwen3 Answer"], OUT_PHRASE)
df["_out_gpt4o"] = safe_contains(df["gpt4o Answer"], OUT_PHRASE)
df["_out_any"] = df[["_out_gt", "_out_qwen", "_out_gpt4o"]].any(axis=1)

# ==== 레이아웃: 탭 두 개 ====
tab_main, tab_out = st.tabs(["🧭 비교 Viewer", "🚫 Out-of-Model"])

# =========================
# 탭 1: 기존 비교 Viewer
# =========================
with tab_main:
    st.markdown("### 🙋 사용자 질문 선택")
    query_list = df["Query_korea"].dropna().tolist()
    selected_query = st.selectbox("🔍 비교할 질문을 선택하세요:", query_list)

    row = df[df["Query_korea"] == selected_query].iloc[0]

    st.markdown(f"### 🏷️ Model: **{row['Model Unique Name']}**")
    st.markdown("### 🙋 사용자 질문")
    st.info(selected_query)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🤖 Qwen3 Answer")
        st.success(row["qwen3 Answer"])
    with col2:
        st.markdown("#### 🤖 GPT-4o Answer")
        st.success(row["gpt4o Answer"])
    with col3:
        st.markdown("#### ✅ Ground Truth")
        st.info(row["GT"])

# =========================
# 탭 2: Out-of-Model 전용
# =========================
with tab_out:
    st.markdown("### 🚫 Out-of-Model 전용 뷰")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 샘플", len(df))
    c2.metric("Out-of-Model (ANY)", int(df["_out_any"].sum()))
    c3.metric("GT 기준", int(df["_out_gt"].sum()))
    c4.metric("Qwen/GPT-4o 기준", int((df["_out_qwen"] | df["_out_gpt4o"]).sum()))

    st.divider()

    # 필터 옵션
    scope = st.radio(
        "필터 기준을 선택하세요",
        ["ANY(하나라도 해당)", "GT만", "Qwen만", "GPT-4o만"],
        horizontal=True
    )

    if scope == "ANY(하나라도 해당)":
        f = df["_out_any"]
    elif scope == "GT만":
        f = df["_out_gt"]
    elif scope == "Qwen만":
        f = df["_out_qwen"] & ~df["_out_gt"] & ~df["_o_]()
