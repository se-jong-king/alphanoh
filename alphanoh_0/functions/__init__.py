from .now import now
from .retriever import retriever

available = [
  {
    "func": now,
    "desc": {
      "name": "now",
      "description": "Get the current date and time.",
      "parameters": {
        "type": "object",
        "properties": {
          "tz": {
            "type": "string",
            "description": "Timezone, e.g. Asia/Seoul"
          }
        },
        "required": ["tz"],
      }
    }
  },

  {
    "func": retriever,
    "desc": {
      "name": "retriever",
      "description": "Retrieve the chunks of the paper named 'A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT'.",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "The user's query about the contents of the paper."
          }
        },
        "required": ["query"],
      }
    }
  },
]