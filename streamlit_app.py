import streamlit as st
import pandas as pd

# 📌 기본 설정
st.set_page_config(page_title="LLM Answer Viewer", layout="wide")
st.title("📄 LLM 응답 비교 Viewer")

# 📁 CSV 파일 경로
CSV_PATH = "RAG_final_v1_extracted_with_query_GT_qwen - RAG_final_v1_extracted_with_query.csv"

# 📥 데이터 로드
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def pick_col(df: pd.DataFrame, candidates: list[str]) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"필요한 컬럼을 찾을 수 없습니다. 후보: {candidates}")

try:
    df = load_data(CSV_PATH)
except Exception as e:
    st.error(f"❌ 파일을 불러올 수 없습니다: {e}")
    st.stop()

# 🔧 컬럼 매핑 (존재하는 이름을 자동 선택)
QUERY_COL = pick_col(df, ["query_kor", "query_korea", "Query_korea", "query"])
QWEN_COL  = pick_col(df, ["Qwen Answer", "qwen3 Answer", "qwen_answer", "qwen"])
GPT4O_COL = pick_col(df, ["gpt4o", "gpt4o Answer", "gpt4o_answer"])
GT_COL    = pick_col(df, ["GT", "Ground Truth", "ground_truth"])

# 🔍 질문 선택
query_list = df[QUERY_COL].dropna().astype(str).tolist()
selected_query = st.selectbox("🔍 비교할 질문을 선택하세요:", query_list)

# 🔄 선택된 행
row = df[df[QUERY_COL] == selected_query].iloc[0]

# 📊 비교 출력
st.markdown("### 🙋 사용자 질문 (한국어)")
st.info(selected_query)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### 🤖 Qwen Answer")
    st.success(str(row[QWEN_COL]))
with col2:
    st.markdown("#### 🤖 GPT-4o")
    st.success(str(row[GPT4O_COL]))
with col3:
    st.markdown("#### ✅ Ground Truth")
    st.info(str(row[GT_COL]))
