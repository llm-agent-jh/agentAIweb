# app_viewer_llm_fullanswer_dual.py
import streamlit as st
import pandas as pd

# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="LLM FullAnswer vs GT (In/Out-of-Model)", layout="wide")
st.title("📄 LLM FullAnswer vs Ground Truth")

# =========================
# 파일 경로
# =========================
INMODEL_CSV  = "GT_with_rag_eval_with_all_models.csv"
OUTMODEL_CSV = "rag_eval_with_all_models_out_of_model.csv"

# =========================
# 유틸
# =========================
@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

REQUIRED = [
    "Folder",
    "GT_Text",
    "chatgpt4o_FullAnswer",
    "qwen3_FullAnswer",
    "claude_FullAnswer",
    "grok4_FullAnswer",
]

NA_PATTERNS = {"not available", "n/a", "na", "none", ""}

def display_text(value) -> str:
    """not available/빈 문자열을 한국어 안내문으로 치환"""
    if value is None:
        return "현재 우리모델에서는 해당 기능을 제공하지 않아"
    s = str(value).strip()
    if s.lower() in NA_PATTERNS:
        return "현재 우리모델에서는 해당 기능을 제공하지 않아"
    return s

def check_required(df: pd.DataFrame, label: str):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        st.error(f"❌ {label} CSV에 필요한 컬럼이 없습니다: {missing}")
        st.stop()

def render_block(label: str, df: pd.DataFrame):
    st.subheader(f"🗂️ {label} Rows (미리보기)")
    preview = df[["Folder", "GT_Text"]].copy()
    preview["chatgpt4o_preview"] = df["chatgpt4o_FullAnswer"].astype(str).str.slice(0, 80) + "..."
    preview["qwen3_preview"]     = df["qwen3_FullAnswer"].astype(str).str.slice(0, 80) + "..."
    preview["claude_preview"]    = df["claude_FullAnswer"].astype(str).str.slice(0, 80) + "..."
    preview["grok4_preview"]     = df["grok4_FullAnswer"].astype(str).str.slice(0, 80) + "..."
    st.dataframe(preview, use_container_width=True, height=320)

    folders = df["Folder"].dropna().astype(str).drop_duplicates().sort_values().tolist()
    sel = st.selectbox(f"🔍 {label} - Folder 선택:", folders, index=0, key=f"pick_{label}")

    row = df[df["Folder"].astype(str) == sel].iloc[0]

    st.markdown("---")
    st.markdown(f"### 📁 Folder: `{row['Folder']}`")

    st.markdown("### ✅ Ground Truth")
    st.success(display_text(row["GT_Text"]))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🤖 ChatGPT-4o")
        st.info(display_text(row["chatgpt4o_FullAnswer"]))
    with c2:
        st.markdown("#### 🤖 Qwen3")
        st.info(display_text(row["qwen3_FullAnswer"]))

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### 🤖 Claude")
        st.info(display_text(row["claude_FullAnswer"]))
    with c4:
        st.markdown("#### 🤖 Grok4")
        st.info(display_text(row["grok4_FullAnswer"]))

# =========================
# 데이터 로드 & 검증
# =========================
in_df  = load_csv(INMODEL_CSV)
out_df = load_csv(OUTMODEL_CSV)

check_required(in_df, "In-Model")
check_required(out_df, "Out-of-Model")

# =========================
# 탭 렌더링
# =========================
tab_in, tab_out = st.tabs(["✅ In-Model", "🚫 Out-of-Model"])
with tab_in:
    render_block("In-Model", in_df)
with tab_out:
    render_block("Out-of-Model", out_df)

st.caption("Tip: 상단 미리보기에서 전체를 훑고, 탭별 Folder를 선택해 GT와 각 LLM의 FullAnswer를 비교하세요.")
