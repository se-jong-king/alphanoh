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
        st.subheader("�����")
        st.markdown(
        "1. [OpenAI API key]�� �Է��ϼ���.\n"  # noqa: E501
        "2. pdf, docx, or txt file�� ���ε� �ϼ���.\n"
        "3. ������ ���� �����ϼ���.\n\n"
        "* �߰� ���� ��� : "
        "4. �Ű����� ����\n"
    )
        st.markdown("---")
        st.header("API Key")
        api_key_input = st.text_input(
            "OpenAI API key�� �Է��ϼ���.",
            type="password",
            placeholder="Paste your OpenAI API key here (sk-...)",
            help="����� API key�� https://platform.openai.com/account/api-keys. ���� ���� �� �ֽ��ϴ�.",  # noqa: E501
            value=os.environ.get("OPENAI_API_KEY", None)
            or st.session_state.get("OPENAI_API_KEY", ""),
        )
        st.markdown("---")

        st.header("Setting(�߰� ��)")
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
            "�Ű������� ���� "
            "�� �ñ��ϸ� [OPENAI](https://platform.openai.com/docs/api-reference/introduction) "  # noqa: E501
            "�� �湮�Ͽ� �ڼ��� �˾ƺ�����.")

        # Functions
        st.subheader("Functions")
        with st.expander("Options"):
            func_checkbox = [st.checkbox(f.get("desc").get("name")) for f in functions.available]

        st.markdown("---")
        st.markdown("# ABOUT")
        st.markdown(
            "[Energy+AI �ٽ�����缺 ����������](https://eaierc.jnu.ac.kr/)"
            "\n2023�⵵ ���� ����ũ�� ĸ���� ������ ������ȸ "
            "AlphaNoh���� ������Դϴ�.")
    
        st.markdown("Made by [se-jong-king](https://github.com/se-jong-king)")
        st.markdown("---")