import streamlit as st
import pandas as pd

# 📌 기본 설정
st.set_page_config(page_title="LLM Answer Viewer", layout="wide")

st.title("📄 LLM 응답 비교 Viewer")

# 📁 업로드 또는 GitHub 연동된 .xlsx 경로 지정
EXCEL_PATH = "RAG_final_v1_extracted_with_query_GT_qwen.xlsx"  # 또는 GitHub raw URL

# 📥 데이터 로드
@st.cache_data
def load_data(path):
    return pd.read_excel(path)

try:
    df = load_data(EXCEL_PATH)
except Exception as e:
    st.error(f"❌ 파일을 불러올 수 없습니다: {e}")
    st.stop()

# 🔍 질문 선택
query_list = df["query"].tolist()
selected_query = st.selectbox("🔍 비교할 질문을 선택하세요:", query_list)

# 🔄 선택된 행 가져오기
row = df[df["query"] == selected_query].iloc[0]

# 📊 세 응답 비교
st.markdown("### 🙋 사용자 질문")
st.info(selected_query)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### 🤖 Qwen Answer")
    st.success(row["Qwen Answer"])
with col2:
    st.markdown("#### 🤖 GPT-4o")
    st.success(row["gpt4o"])
with col3:
    st.markdown("#### ✅ Ground Truth")
    st.info(row["GT"])
