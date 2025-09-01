# app_viewer_llm_fullanswer.py
import streamlit as st
import pandas as pd

# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="LLM FullAnswer vs GT", layout="wide")
st.title("📄 LLM FullAnswer vs Ground Truth")

CSV_PATH = "GT_with_rag_eval_with_all_models.csv"  # ← 새 파일명

# =========================
# 데이터 로드
# =========================
@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

df = load_csv(CSV_PATH)

# 필요한 컬럼(없으면 경고)
needed = [
    "Folder",
    "GT_Text",
    "chatgpt4o_FullAnswer",
    "qwen3_FullAnswer",
    "claude_FullAnswer",
    "grok4_FullAnswer",
]
missing = [c for c in needed if c not in df.columns]
if missing:
    st.error(f"❌ CSV에 필요한 컬럼이 없습니다: {missing}")
    st.stop()

# =========================
# 상단 미리보기 + 선택
# =========================
st.subheader("🗂️ Rows (미리보기)")
st.dataframe(
    df[["Folder", "GT_Text"]].assign(
        chatgpt4o_preview=df["chatgpt4o_FullAnswer"].astype(str).str.slice(0, 80) + "...",
        qwen3_preview=df["qwen3_FullAnswer"].astype(str).str.slice(0, 80) + "...",
        claude_preview=df["claude_FullAnswer"].astype(str).str.slice(0, 80) + "...",
        grok4_preview=df["grok4_FullAnswer"].astype(str).str.slice(0, 80) + "...",
    ),
    use_container_width=True,
    height=320,
)

# Folder 기준 선택
folders = df["Folder"].dropna().astype(str).drop_duplicates().sort_values().tolist()
sel = st.selectbox("🔍 Folder 선택:", folders, index=0)

row = df[df["Folder"].astype(str) == sel].iloc[0]

# =========================
# 본문 출력 (GT + 각 LLM FullAnswer)
# =========================
st.markdown("---")
st.markdown(f"### 📁 Folder: `{row['Folder']}`")

st.markdown("### ✅ Ground Truth")
st.success(str(row["GT_Text"]))

c1, c2 = st.columns(2)
with c1:
    st.markdown("#### 🤖 ChatGPT-4o")
    st.info(str(row["chatgpt4o_FullAnswer"]))
with c2:
    st.markdown("#### 🤖 Qwen3")
    st.info(str(row["qwen3_FullAnswer"]))

c3, c4 = st.columns(2)
with c3:
    st.markdown("#### 🤖 Claude")
    st.info(str(row["claude_FullAnswer"]))
with c4:
    st.markdown("#### 🤖 Grok4")
    st.info(str(row["grok4_FullAnswer"]))

st.caption("Tip: 상단 표에서 전체 행을 훑어보고, Folder 드롭다운으로 상세 비교하세요.")
