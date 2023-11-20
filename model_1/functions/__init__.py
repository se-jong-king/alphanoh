from .retriever import retriever

available = [
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