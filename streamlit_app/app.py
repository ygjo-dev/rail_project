import sys
import os
import time

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import ollama

from py2neo import Graph

from utils.config_loader import load_config

from streamlit_app.map_view import render_map
from workflow import run_workflow


# --------------------------------------------------
# Config
# --------------------------------------------------

cfg = load_config()

OLLAMA_API_URL = cfg["ollama"]["api_url"]

PARSER_MODEL = cfg["ollama"]["parser_model"]
ANSWER_MODEL = cfg["ollama"]["answer_model"]

NEO4J_URI = cfg["neo4j"]["uri"]
NEO4J_USER = cfg["neo4j"]["user"]
NEO4J_PASSWORD = cfg["neo4j"]["password"]

ollama.api_url = OLLAMA_API_URL

graph = Graph(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

# --------------------------------------------------
# UI
# --------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="철도 Agent"
)

st.title("철도 Agent")

render_map(graph)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header(
    "철도 관련 질문"
)

user_question = st.sidebar.text_input(
    "예: 서울에서 부산까지 KTX 연결되어 있어?"
)

if user_question:

    total_start = time.perf_counter()

    try:

        result = run_workflow(
            question=user_question,
            graph=graph,
            parser_model=PARSER_MODEL,
            answer_model=ANSWER_MODEL
        )

        if not result["success"]:

            st.sidebar.warning(
                result["error"]
            )

            st.stop()

        st.sidebar.subheader(
            "🔍 디버그: LLM 파싱 결과"
        )

        st.sidebar.json(
            result["parsed"]
        )

        st.sidebar.markdown(
            "### 답변"
        )

        st.sidebar.write(
            result["answer"]
        )

        total_elapsed = (
            time.perf_counter()
            - total_start
        )

        st.sidebar.divider()

        st.sidebar.info(
            f"총 소요 시간: {total_elapsed:.2f}초"
        )

        st.sidebar.caption(
            f"• 파싱: "
            f"{result['metrics']['parse_time']:.2f}초 "
            f"({PARSER_MODEL})"
        )

        st.sidebar.caption(
            f"• Skill 실행: "
            f"{result['metrics']['skill_time']:.2f}초"
        )

        st.sidebar.caption(
            f"• 답변 생성: "
            f"{result['metrics']['answer_time']:.2f}초 "
            f"({ANSWER_MODEL})"
        )

    except Exception as e:

        total_elapsed = (
            time.perf_counter()
            - total_start
        )

        st.sidebar.error(
            "처리 중 오류가 발생했습니다."
        )

        st.sidebar.code(
            str(e)
        )

        st.sidebar.info(
            f"총 경과 시간: "
            f"{total_elapsed:.2f}초"
        )