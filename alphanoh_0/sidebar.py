# -*- coding: euc-kr -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')


import streamlit as st
import os
from utils.streamlit import undo
import functions

def sidebar():
    # Sidebar for parameters
    with st.sidebar:
        st.markdown("# AlphaNoh")
        st.subheader("사용방법")
        st.markdown(
        "1. [OpenAI API key]를 입력하세요.\n"  # noqa: E501
        "2. pdf, docx, or txt file을 업로드 하세요.\n"
        "3. 문서에 관해 질문하세요.\n\n"
        "* 추가 예정 기능 : "
        "4. 매개변수 조절\n"
    )
        st.markdown("---")
        st.header("API Key")
        api_key_input = st.text_input(
            "OpenAI API key를 입력하세요.",
            type="password",
            placeholder="Paste your OpenAI API key here (sk-...)",
            help="당신의 API key를 https://platform.openai.com/account/api-keys. 에서 얻을 수 있습니다.",  # noqa: E501
            value=os.environ.get("OPENAI_API_KEY", None)
            or st.session_state.get("OPENAI_API_KEY", ""),
        )
        st.markdown("---")

        st.header("Setting(추가 중)")
        # Role selection and Undo
        st.subheader("Chat")
        with st.expander("role"):
            chat_role = st.selectbox("type", ["system", "assistant", "user", "function"], index=2)
            st.button("Undo", on_click=undo)

        st.subheader("Visible")
        with st.expander("options"):
            system_checkbox = st.checkbox("system", value=True)
            _call_checkbox = st.checkbox("function", value=True)
    

        # ChatCompletion parameters
        st.subheader("Parameters")
        with st.expander("Options"):
            chat_params = {
            "model": st.selectbox("model", ["gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613", "gpt-4-0613", "gpt-4-32k-0613"]),
            "n": st.number_input("n", min_value=1, value=1),
            "temperature": st.slider("temperature", min_value=0.0, max_value=2.0, value=1.0),
            "max_tokens": st.number_input("max_tokens", min_value=1, value=512),
            "top_p": st.slider("top_p", min_value=0.0, max_value=1.0, value=1.0),
            "presence_penalty": st.slider("presence_penalty", min_value=-2.0, max_value=2.0, value=0.0),
            "frequency_penalty": st.slider("frequency_penalty", min_value=-2.0, max_value=2.0, value=0.0),
            "stream": True,
        }
        st.markdown(
            "매개변수에 대해 "
            "더 궁금하면 [OPENAI](https://platform.openai.com/docs/api-reference/introduction) "  # noqa: E501
            "에 방문하여 자세히 알아보세요.")

        # Functions
        st.subheader("Functions")
        with st.expander("Options"):
            func_checkbox = [st.checkbox(f.get("desc").get("name")) for f in functions.available]

        st.markdown("---")
        st.markdown("# ABOUT")
        st.markdown(
            "[Energy+AI 핵심인재양성 교육연구단](https://eaierc.jnu.ac.kr/)"
            "\n2023년도 동계 마이크로 캡스톤 디자인 경진대회 "
            "AlphaNoh팀의 결과물입니다.")
    
        st.markdown("Made by [se-jong-king](https://github.com/se-jong-king)")
        st.markdown("---")