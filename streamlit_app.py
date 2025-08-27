import streamlit as st
import pandas as pd
import os
st.cache_data.clear()
# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="LLM Answer Viewer", layout="wide")
st.title("📄 LLM 응답 비교 Viewer")

# -------------------------
# 파일 경로
# -------------------------
BASE_DIR = "."  # 두 파일이 같은 경로에 있을 경우
MAIN_FILE = os.path.join(BASE_DIR, "RAG_final_v1_extracted_with_query_GT_qwen.csv")
OUT_FILE  = os.path.join(BASE_DIR, "RAG_outofmodel_only.csv")

# =========================
# 유틸
# =========================
@st.cache_data
def load_table(path: str) -> pd.DataFrame:
    if path.lower().endswith(".xlsx"):
        return pd.read_excel(path)
    return pd.read_csv(path)

# =========================
# 데이터 로드
# =========================
df_main = load_table(MAIN_FILE)
df_out  = load_table(OUT_FILE)

# =========================
# 메인 뷰어 탭
# =========================
tab_main, tab_out = st.tabs(["🧭 비교 Viewer (메인)", "🚫 Out-of-Model (별도 파일)"])

# -------------------------
# 탭 1: 메인 비교 뷰어
# -------------------------
with tab_main:
    query_list = df_main["query_kor"].dropna().tolist()
    selected_query = st.selectbox("🔍 비교할 질문을 선택하세요:", query_list)

    row = df_main[df_main["query_kor"] == selected_query].iloc[0]

    st.markdown("### 🙋 사용자 질문")
    st.info(selected_query)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🤖 Qwen3 Answer")
        st.success(str(row["qwen3 Answer"]))
    with c2:
        st.markdown("#### 🤖 GPT-4o Answer")
        st.success(str(row["gpt4o Answer"]))
    with c3:
        st.markdown("#### ✅ Ground Truth")
        st.info(str(row["GT"]))

# -------------------------
# 탭 2: Out-of-Model 뷰
# -------------------------
with tab_out:
    st.markdown("### 🚫 Out-of-Model 전용 뷰")

    # 리스트 미리보기
    st.dataframe(df_out[["Model Unique Name", "Category", "Query_korea", "qwen3 Answer", "gpt4o Answer", "GT"]],
                 use_container_width=True, height=420)

    # 질문 선택 상세보기
    query_out_list = df_out["Query_korea"].dropna().tolist()
    selected_out = st.selectbox("🔍 Out-of-Model 질문 선택:", query_out_list)

    row_o = df_out[df_out["Query_korea"] == selected_out].iloc[0]

    st.markdown(f"**Model**: {row_o['Model Unique Name']} | **Category**: {row_o['Category']}")
    st.info(row_o["Query_korea"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**GT**")
        st.warning(str(row_o["GT"]))
    with c2:
        st.markdown("**Qwen3 Answer**")
        st.warning(str(row_o["qwen3 Answer"]))
    with c3:
        st.markdown("**GPT-4o Answer**")
        st.warning(str(row_o["gpt4o Answer"]))
