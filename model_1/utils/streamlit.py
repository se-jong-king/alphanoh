import streamlit as st
import json
from .openai import Stream2Msgs
import functions

def append_history(msgs:Stream2Msgs, i:int):
  msg = msgs.msgs[i]
  if content := msg.get("content", ""):
    st.session_state.messages.append({
      "role": "assistant",
      "content": content,
    })
  if f_name := msg.get("function_call", {}).get("name", ""):
    f_args = json.loads(msg.get("function_call").get("arguments"))
    st.session_state.messages.append({
      "role": "assistant",
      "content": "",
      "function_call": {
        "name": f_name,
        "arguments": json.dumps(f_args)
      }
    })
    for f in functions.available:
      if f.get("desc").get("name") == f_name:
        st.session_state.messages.append({
          "role": "function",
          "name": f_name,
          "content": f.get("func")(**f_args)
        })

def undo():
  st.session_state.messages = st.session_state.messages[:-1]

def stream_display(response:iter, n:int=1):
  # To concatenate tokens in delta
  full_msgs = Stream2Msgs(n)
  # Placeholders
  with st.chat_message("assistant"):
    placeholders = [
      {
        "text": st.empty(),
        "button": st.button(
          f"Choose Answer No. {i+1}",
          on_click=append_history, args=[full_msgs, i]
        ) if n > 1 else None,
        "_divider": st.divider() if n > 1 else None,
      } for i in range(n)
    ]
  # Write delta on placeholders
  for res in response:
    i, msg = full_msgs(res)
    placeholders[i].get("text").write(msg.get("content") + "▌")
  # Write full message on placeholders
  for i in range(n):
    placeholders[i].get("text").write(full_msgs.msgs[i].get("content"))
    if f_name := full_msgs.msgs[i].get("function_call", {}).get("name", ""):
      f_args = full_msgs.msgs[i].get("function_call").get("arguments", "")
      placeholders[i].get("text").write(f"function_call: {f_name}(), args: {f_args}")
  if n == 1:
    append_history(full_msgs, 0)
    st.rerun()