import streamlit as st
import os
import json
import re
from pathlib import Path

# 🔧 사용자 정의: JSON 폴더 경로
DATA_PATH = Path("results")

# 🔁 모델 키 → 이름 매핑
MODEL_MAP = {
    "llm_a": "claude_sonnet4",
    "llm_b": "chatgpt4o",
    "llm_c": "gemini_pro"
}

# 📐 페이지 설정
st.set_page_config(layout="wide", page_title="AgentAI Viewer", page_icon="🧠")

# ✅ 📁 페이지 선택 추가
st.sidebar.markdown("### 📁 페이지 선택")
page = st.sidebar.radio("페이지를 선택하세요", [
    "응답 비교 보기",
    "향후 피드백 방향성",
    "예측 결과 비교",
    "prompt_regenerated 비교"
])

# ───────────────────────────────────────────────────────────
# ✅ 1. 응답 비교 보기ㄴㄴㄴ
# ───────────────────────────────────────────────────────────
if page == "응답 비교 보기":
    json_files = sorted(DATA_PATH.glob("*.json"))
    query_map = {f.stem: f for f in json_files}

    st.sidebar.title("🔍 Query Navigation")
    selected_query = st.sidebar.selectbox("Select Query", list(query_map.keys()))

    with st.sidebar.expander("📋 평가 기준 보기"):
        st.markdown("""
**🧪 평가 기준 (각 항목당 10점 만점)**

| 번호 | 항목 | 설명 |
|------|------|------|
| 1 | 명확성 및 가독성 | 설명이 명확하고 구조적으로 잘 정리되었는가? |
| 2 | 정확성 및 완전성 | 요구된 모든 항목이 빠짐없이 포함되었는가? |
| 3 | CNAPS 스타일 워크플로우 | 분기(branch), 병합(merge) 등 시냅스 구조가 반영되었는가? |
| 4 | 제공 모델만 사용 | 문제에서 제시한 모델만을 사용했는가? |
| 5 | 해석 가능성과 설득력 | 선택 모델의 근거와 설명이 설득력 있었는가? |
""")

    with open(query_map[selected_query], 'r') as f:
        data = json.load(f)

    query_text = data.get("query_text", "")
    responses = data.get("responses", {})
    votes = data.get("votes", {})
    majority = data.get("majority_vote", "")

    ask_match = re.search(r"A user asks:\n[\"“](.+?)[\"”]", query_text, re.DOTALL)
    user_ask = ask_match.group(1).strip() if ask_match else "(사용자 질문을 찾을 수 없습니다.)"

    model_block_match = re.search(r"### Recommended AI Models:\s*\n(.+)", query_text, re.DOTALL)
    models_raw = model_block_match.group(1).strip() if model_block_match else "(모델 목록 없음)"
    models_clean = re.findall(r"- \*\*(.*?)\*\*\n\s*Paper: (.*)", models_raw)
    models_md = "\n".join([f"- **{name}**\n  Paper: {link}" for name, link in models_clean]) if models_clean else models_raw

    st.markdown("## 🙋 사용자 질문")
    st.info(f"**\"{user_ask}\"**")

    st.markdown("## 🧠 추천된 AI 모델 목록")
    st.code(models_md, language="markdown")

    st.markdown("## 🤖 Model Responses")
    for raw_key in ["llm_a", "llm_b", "llm_c"]:
        response = responses.get(raw_key, "(No response found)")
        mapped_name = MODEL_MAP.get(raw_key, raw_key)
        voted_by = [model for model, v in votes.items() if v == raw_key]
        majority_flag = "🌟 **Majority Vote**" if raw_key == majority else ""

        with st.expander(f"🧠 {mapped_name}", expanded=True):
            st.markdown(response, unsafe_allow_html=True)
            st.markdown(f"✅ **Voted by**: {', '.join(voted_by) if voted_by else 'None'}")
            if majority_flag:
                st.markdown(majority_flag)

# ───────────────────────────────────────────────────────────
# ✅ 2. 향후 피드백 방향성
# ───────────────────────────────────────────────────────────
elif page == "향후 피드백 방향성":
    st.title("📈 향후 피드백 방향성: RAG 성능 향상 중심 전략")

    st.markdown("""
---

## 🎯 목표 재정의

기존에는 출력 양식의 구조화와 CNAPS 스타일 응답 일관성에 초점을 맞췄다면,  
**향후에는 Retrieval-Augmented Generation (RAG) 성능 향상 자체를 핵심 목표로 전환**합니다.

---

## 🧠 핵심 전략

- 단순히 양식을 잘 맞추는 것에 그치지 않고,  
  **정확하고 정보 기반의 응답을 생성할 수 있는 retrieval-aware fine-tuning** 또는  
  **강건한 multi-hop retrieval chain 학습 구조**로 발전

---

## 📘 참고 사례 (성능 중심 RAG 연구)

- [CoRAG (Chain-of-Retrieval)](https://arxiv.org/pdf/2501.14342): step-by-step 검색 흐름을 생성하며 응답 품질 극대화
- RbFT: retrieval 오류에 강건한 fine-tuning 구조
- Invar-RAG / OpenRAG: retriever와 generator를 end-to-end로 동시 최적화
- IterKey: sparse retrieval에서도 iterative 방식으로 성능 보강

---

## ✅ 요약

앞으로는 **LLM이 단순 생성자가 아니라, 능동적 검색 행위자로 작동할 수 있도록**  
retrieval을 포함한 학습 구조와 평가 방식을 강화하는 방향으로 피드백과 개선을 이어갈 예정입니다.
""")

# ───────────────────────────────────────────────────────────
# ✅ 3. 예측 결과 비교 (인덱스 기반)
# ───────────────────────────────────────────────────────────
elif page == "예측 결과 비교":
    st.title("📊 LLM 예측 결과 vs 정답 비교")

    pred_file_path = "results/generated_predictions_extracted.json"

    if os.path.exists(pred_file_path):
        with open(pred_file_path, "r", encoding="utf-8") as f:
            prediction_data = json.load(f)

        st.sidebar.markdown("### 🔢 항목 선택")
        example_idx = st.sidebar.number_input("인덱스 선택", min_value=0, max_value=len(prediction_data)-1, value=0, step=1)
        example = prediction_data[example_idx]

        st.markdown("## 🙋 Prompt (User Input)")
        st.code(example["prompt"], language="markdown")

        st.markdown("## 🤖 Predict (LLM Output)")
        st.success(example["predict"])

        st.markdown("## ✅ Label (Ground Truth)")
        st.info(example["label"])
    else:
        st.warning("📁 results/generated_predictions_extracted.json 파일이 존재하지 않습니다.")


# ───────────────────────────────────────────────────────────
# ✅ 4. Prompt Regenerated 비교
# ───────────────────────────────────────────────────────────
elif page == "prompt_regenerated 비교":
    st.title("📝 Query1: Prompt (vanilla vs regenerated) 비교")

    # JSON 경로
    prompt_json_path = Path("results/prompt_comparsion.json")
    if not prompt_json_path.exists():
        st.warning("📁 results/merged_query1.json 파일이 존재하지 않습니다.")
    else:
        with open(prompt_json_path, "r", encoding="utf-8") as f:
            prompt_data = json.load(f)

        # 모델 선택
        st.sidebar.markdown("### 🧠 모델 선택")
        model_names = sorted(prompt_data.keys())
        selected_model = st.sidebar.selectbox("모델을 선택하세요", model_names)

        # 해당 모델의 vanilla / regenerated 쿼리
        vanilla_query = prompt_data[selected_model].get("vanilla", "(vanilla 쿼리 없음)")
        regenerated_query = prompt_data[selected_model].get("regenerated", "(regenerated 쿼리 없음)")

        st.markdown(f"### 📌 선택한 모델: `{selected_model}`")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🧾 Vanilla Prompt")
            st.code(vanilla_query, language="markdown")
        with col2:
            st.markdown("#### ✨ Regenerated Prompt")
            st.code(regenerated_query, language="markdown")
