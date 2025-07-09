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

# 페이지 선택
page = st.sidebar.radio("페이지를 선택하세요", ["응답 비교 보기", "향후 피드백 방향성", "특정 결과 보기 (테스트 전용)"])

if page == "응답 비교 보기":
    query_ids = [item["query_id"] for item in json_data]
    selected_query = st.sidebar.selectbox("🔍 Select Query", query_ids)

    # 해당 쿼리 선택
    query_obj = next(item for item in json_data if item["query_id"] == selected_query)

    # 쿼리 표시
    st.markdown("## 📝 Query")
    st.markdown(f"```
{query_obj['query_text']}
```")

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

elif page == "향후 피드백 방향성":
    st.title("🧭 향후 피드백 방향성 및 개선 전략")

    st.markdown("""
---

### 🔎 문제점 정리

1. **Mermaid 기반 흐름도 생성 오류**  
   일부 LLM(특히 Gemini)은 Mermaid 형식의 시각적 flow 생성을 안정적으로 처리하지 못합니다.  
   → 연결 구조만 요구했음에도 불필요한 입력 채널이나 low-level 정보가 과도하게 포함됩니다.

2. **Low-level 중심 응답 경향**  
   사용자는 high-level 중심의 CNAPS-style 흐름을 요구했으나, 모델은 처리 세부 단계에 집중하여 응답의 가독성과 전략성이 저하됩니다.

3. **RAG 추천 모델의 과사용**  
   RAG로 Top-3 모델을 추천했을 때, 대부분 1~2개는 유효하지만  
   나머지 불필요한 모델까지 억지로 사용하려는 경향이 나타났습니다.

---

### ✅ 해결 방안: Refine 기반 개선 구조

- 사용자의 피드백을 기반으로 LLM이 동일 질문에 대해 응답을 다시 생성
- Mermaid 형식, 불필요한 모델 제거, high-level 구조 강조 등 문제를 반영하여 품질을 향상
- 향후 개선 응답은 기존 응답과 비교하고 선택할 수 있는 구조로 설계

📌 이 루프를 통해 LLM 답변의 구조화, 간결성, 전략성을 지속적으로 개선할 수 있습니다.

---
""")

elif page == "특정 결과 보기 (테스트 전용)":
    st.title("🧪 단일 JSON 평가 결과 뷰어 (테스트용)")
    test_file = st.sidebar.text_input("JSON 파일 경로를 입력하세요", value="Inpainting-CTSDG-Places2.json")

    if os.path.exists(test_file):
        with open(test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        st.markdown("### 🙋 사용자 질문")
        user_question = re.search(r'A user asks:\n["“](.+?)["”]', data.get("query_text", ""), re.DOTALL)
        st.info(user_question.group(1) if user_question else data.get("query_text", "(질문 없음)"))

        st.markdown("### 🤖 Claude 응답")
        st.markdown(data["responses"].get("llm_a", "(없음)"))

        st.markdown("### 🤖 Gemini 응답")
        st.markdown(data["responses"].get("llm_b", "(없음)"))

        st.markdown("---")
        st.markdown("### 🏆 선택 결과")
        st.markdown(f"**Best by Score:** {data.get('best_by_score', '-')}")
        st.markdown(f"**Majority Vote:** {data.get('majority_vote', '-')}")

        st.markdown("### 💬 각 모델의 선택 이유")
        for k, v in data.get("rationales", {}).items():
            st.markdown(f"**{k}**: {v}")
    else:
        st.warning("해당 경로의 JSON 파일이 존재하지 않습니다.")
