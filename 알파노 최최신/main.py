# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

#Streamlit 설정
import streamlit as st
import openai
import os
from utils.streamlit import append_history, undo, stream_display
from utils.openai import Stream2Msgs
import functions

from alphanoh.ui import (
    wrap_doc_in_html,
    is_query_valid,
    is_file_valid,
    is_open_ai_key_valid,
    display_file_read_error,
)

from alphanoh.caching import bootstrap_caching

from alphanoh.parsing import read_file

from alphanoh.parsing import read_file
from alphanoh.chunking import chunk_file
from alphanoh.embedding import embed_files

# Enable caching for expensive functions
bootstrap_caching()

st.title("Chatbot")
st.caption("A streamlit chatbot powered by OpenAI LLM")


# Initialize chat history
if "messages" not in st.session_state:
  st.session_state.messages = []

# Sidebar for parameters
with st.sidebar:
    st.markdown("# AlphaNoh")
    st.subheader("사용방법")
    st.markdown(
    "1. [OpenAI API key]를 입력하세요.\n"  # noqa: E501
    "2. pdf, docx, or txt file을 업로드 하세요.\n"
    "3. 문서에 관해 질문하세요.\n"
    "4. 매개변수를 조절하면서 질문하세요.\n"
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

    #file upload
    st.header("파일")
    uploaded_file = st.file_uploader(
    "pdf, docx, or txt file을 여기에 업로드 하세요.",
    type=["pdf", "docx", "txt"],
    help="스캔된 문서는 아직 지원이 되지 않습니다.",
    )
    st.markdown("---")

    st.header("Setting")
    # Role selection and Undo
    st.subheader("Chat")
    with st.expander("role"):
      chat_role = st.selectbox("type", ["system", "assistant", "user", "function"], index=2)
      st.button("Undo", on_click=undo)

    st.subheader("Visible")
    with st.expander("options"):
      system_checkbox = st.checkbox("system", value=True)
      f_call_checkbox = st.checkbox("function", value=True)
    

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

    st.subheader("Advanced option")
    with st.expander("Options"):
     return_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
     show_full_doc = st.checkbox("업로드한 문서 확인하기")


    st.markdown("---")
    st.markdown("# ABOUT")
    st.markdown(
        "[Energy+AI 핵심인재양성 교육연구단](https://eaierc.jnu.ac.kr/)"
        "\n2023년도 동계 마이크로 캡스톤 디자인 경진대회 "
        "AlphaNoh팀의 결과물입니다.")
    
    st.markdown("Made by [se-jong-king](https://github.com/se-jong-king)")
    st.markdown("---")
    


    
# Display messages in history
roles = ["user", "assistant"]
if system_checkbox:
  roles.append("system")
if f_call_checkbox:
  roles.append("function")

for msg in st.session_state.messages:
  if (role := msg.get("role")) in roles:
    if content := msg.get("content", ""):
      with st.chat_message(role):
        st.write(content)
    if f_call_checkbox:
      if f_name := msg.get("function_call", {}).get("name", ""):
        f_args = msg.get("function_call").get("arguments", "")
        with st.chat_message(role):
          st.write(f"function_call: {f_name}(), args: {f_args}")

# In the case of the role of the last entry of the history is function
if st.session_state.messages:
  if st.session_state.messages[-1].get("role") == "function":
    # ChatCompletion
    response = openai.ChatCompletion.create(
      messages=st.session_state.messages,
      **chat_params
    )
    # Number of choices
    n = chat_params.get("n")
    # Stream display
    stream_display(response, n)

# Chat input
if prompt := st.chat_input("What is up?"):
  # User message
  user_msg = {
    "role": chat_role,
    "content": prompt,
  }
  # function role need name
  if chat_role == "function":
    user_msg.update({"name": "dummy"})
  # Display user message
  with st.chat_message(chat_role):
    st.write(prompt)
  # Append to history
  st.session_state.messages.append(user_msg)

  if chat_role == "user":
    # parameter `functions`
    func_desc = [functions.available[i].get("desc") for i, check in enumerate(func_checkbox) if check]
    if func_desc:
      chat_params["functions"] = func_desc
    else:
      chat_params.pop("functions", None)

    # ChatCompletion
    response = openai.ChatCompletion.create(
      messages=st.session_state.messages,
      **chat_params
    )
    # Number of choices
    n = chat_params.get("n")
    # Stream display
    stream_display(response, n)


if not uploaded_file:
    st.stop()

try:
    file = read_file(uploaded_file)
except Exception as e:
    display_file_read_error(e, file_name=uploaded_file.name)

chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)

if not is_file_valid(file):
    st.stop()

if show_full_doc:
    with st.expander("Document"):
        # Hack to get around st.markdown rendering LaTeX
        st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)