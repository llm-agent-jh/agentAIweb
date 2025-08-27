import streamlit as st
import pandas as pd
import os

# =========================
# 캐시 초기화 (선택)
# =========================
st.cache_data.clear()

# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="LLM Answer Viewer", layout="wide")
st.title("📄 LLM 응답 비교 Viewer")

# -------------------------
# 파일 경로
# -------------------------
BASE_DIR = "."
MAIN_FILE = os.path.join(BASE_DIR, "RAG_final_v1_extracted_with_query_GT_qwen.csv")
OUT_FILE  = os.path.join(BASE_DIR, "RAG_outofmodel_only.csv")

# =========================
# 유틸 함수
# =========================
@st.cache_data
def load_table(path: str) -> pd.DataFrame:
    if path.lower().endswith(".xlsx"):
        return pd.read_excel(path)
    return pd.read_csv(path)

def safe_get(row, col):
    try:
        return "" if pd.isna(row[col]) else str(row[col])
    except KeyError:
        return f"[❌ Missing: {col}]"
    except Exception as e:
        return f"[❌ Error: {e}]"

# =========================
# 데이터 로드 + 컬럼 정리
# =========================
df_main = load_table(MAIN_FILE)
df_main.columns = df_main.columns.str.strip()

df_out = load_table(OUT_FILE)
df_out.columns = df_out.columns.str.strip()

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

    matched = df_main[df_main["query_kor"] == selected_query]
    if not matched.empty:
        row = matched.iloc[0]

        st.markdown("### 🙋 사용자 질문")
        st.info(selected_query)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 🤖 Qwen3 Answer")
            st.success(safe_get(row, "Qwen Answer"))
        with c2:
            st.markdown("#### 🤖 GPT-4o Answer")
            st.success(safe_get(row, "gpt4o"))
        with c3:
            st.markdown("#### ✅ Ground Truth")
            st.info(safe_get(row, "GT"))
    else:
        st.warning("선택한 질문에 대한 데이터를 찾을 수 없습니다.")

# -------------------------
# 탭 2: Out-of-Model 뷰
# -------------------------
with tab_out:
    st.markdown("### 🚫 Out-of-Model 전용 뷰")

    # 정확한 컬럼만 사용
    preview_cols = ["Model Unique Name", "Category", "Query_korea", "qwen3 Answer", "gpt4o Answer", "GT"]
    
    # 안전하게 DataFrame 표시
    st.dataframe(df_out[preview_cols], use_container_width=True, height=420)
    
        query_out_list = df_out["query_kor"].dropna().tolist()
        selected_out = st.selectbox("🔍 Out-of-Model 질문 선택:", query_out_list)
    
        matched_o = df_out[df_out["query_kor"] == selected_out]
        if not matched_o.empty:
            row_o = matched_o.iloc[0]

        st.markdown(f"**Model**: {row_o['Model Unique Name']} | **Category**: {row_o['Category']}")
        st.info(row_o["query_kor"])

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**GT**")
            st.warning(safe_get(row_o, "GT"))
        with c2:
            st.markdown("**Qwen3 Answer**")
            st.warning(safe_get(row_o, "Qwen Answer"))
        with c3:
            st.markdown("**GPT-4o Answer**")
            st.warning(safe_get(row_o, "gpt4o Answer"))
    else:
        st.warning("선택한 질문에 대한 데이터를 찾을 수 없습니다.")
