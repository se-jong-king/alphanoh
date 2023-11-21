class Stream2Msgs:
  def __init__(self, n=1, role="assistant"):
    self.msgs = [
      {
        "role": role,
        "content": "",
        "function_call": {
          "name": "",
          "arguments": "",
        },
      } for _ in range(n)
    ]
  
  def input(self, res):
    i = res.choices[0].index
    delta = res.choices[0].delta
    if content := delta.get("content", ""):
      self.msgs[i]["content"] += content
    if f_call := delta.get("function_call", {}):
      name = f_call.get("name", "")
      self.msgs[i]["function_call"]["name"] += name
      args = f_call.get("arguments", "")
      self.msgs[i]["function_call"]["arguments"] += args
    return i

  def __call__(self, res):
    i = self.input(res)
    return i, self.msgs[i]