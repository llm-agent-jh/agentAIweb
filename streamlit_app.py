import streamlit as st
import os
import json
import re
from pathlib import Path

# --- 기본 매핑 설정 ---
LLM_LABELS = {
    "llm_a": "claude",
    "llm_b": "gemini",
    "llm_c": "(unused)"
}

LLM_COLORS = {
    "claude": "#FFF8DC",
    "gemini": "#E6FFE6",
    "(unused)": "#f0f0f0"
}

# --- JSON 로딩 ---
@st.cache_data
def load_json_files(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".json")]
    data = []
    for f in files:
        with open(os.path.join(directory, f), "r", encoding="utf-8") as j:
            data.append(json.load(j))
    return data

# --- Streamlit UI 구성 ---
st.set_page_config(layout="wide")
st.title("🧠 LLM CNAPS Evaluation Viewer")

# JSON 폴더 경로 입력
json_dir = st.sidebar.text_input("📁 JSON Directory", value="./results")
json_data = load_json_files(json_dir)

query_ids = [item["query_id"] for item in json_data]
selected_query = st.sidebar.selectbox("🔍 Select Query", query_ids)

# 해당 쿼리 선택
query_obj = next(item for item in json_data if item["query_id"] == selected_query)

# 쿼리 표시
st.markdown("## 📝 Query")
st.markdown(f"```\n{query_obj['query_text']}\n```")

# 응답 렌더링
st.markdown("---")
st.markdown("## 🤖 LLM Responses")
responses = query_obj["responses"]
columns = st.columns(2)

for i, llm_key in enumerate(["llm_a", "llm_b"]):
    model_name = LLM_LABELS[llm_key]
    with columns[i]:
        st.markdown(f"### {model_name.title()} Response")
        st.markdown(
            f"<div style='background-color:{LLM_COLORS[model_name]}; padding:10px; border-radius:5px'>"
            f"<pre style='white-space:pre-wrap'>{responses[llm_key]}</pre></div>",
            unsafe_allow_html=True
        )

# 최종 선택 결과
st.markdown("---")
st.markdown("## 🏆 Final Selection")

best_model = LLM_LABELS.get(query_obj.get("best_by_score"), "unknown")
majority_vote = LLM_LABELS.get(query_obj.get("majority_vote"), "unknown")

st.success(f"**Best by Score:** {best_model.title()}")
st.info(f"**Majority Vote:** {majority_vote.title()}")

# 각 모델이 선택한 이유
st.markdown("---")
st.markdown("## 💬 Rationales by Model")
rationales = query_obj.get("rationales", {})
for model_key, text in rationales.items():
    readable_name = model_key.split("/")[-1]  # e.g., "gpt-4o"
    with st.sidebar:
        st.markdown(f"### 🧩 {readable_name} Rationale")
        st.markdown(f"<div style='background-color:#f4f4f4; padding:8px; border-radius:5px'><small>{text}</small></div>", unsafe_allow_html=True)
