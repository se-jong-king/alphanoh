# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

import streamlit as st
import openai
from utils.streamlit import append_history, undo, stream_display
from utils.openai import Stream2Msgs
import functions

st.title("MODEL_1")
st.caption("made by AlphaNoh")

# OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Initialize chat history
if "messages" not in st.session_state:
  st.session_state.messages = []

# Sidebar for parameters
with st.sidebar:
  st.markdown("# Model_1")
  st.subheader("사용방법")
  st.markdown(
    "1. function에서 retriever를 선택하세요.\n"
    "2. A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT.\n"
    "문서에 관해 질문하세요.\n"
    "3. 매개변수를 조절하면서 질문해보세요.\n"
    )

  # Role selection and Undo
  st.header("Chat")
  chat_role = st.selectbox("role", ["system", "assistant", "user", "function"], index=2)
  st.button("Undo", on_click=undo)

  st.subheader("Visible")
  system_checkbox = st.checkbox("system", value=True)
  f_call_checkbox = st.checkbox("function", value=True)
  
  # ChatCompletion parameters
  st.header("Parameters")
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
  st.header("Functions")
  func_checkbox = [st.checkbox(f.get("desc").get("name")) for f in functions.available]

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