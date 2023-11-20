from openai.embeddings_utils import get_embedding, cosine_similarity
import numpy as np
import pandas as pd
from ast import literal_eval

def retriever(query:str):
  top_n = 3
  df = pd.read_csv("./data/2302.11382v1_embeddings.csv", index_col=0)
  df["embedding"] = df.embedding.apply(literal_eval).apply(np.array)
  query_embedding = get_embedding(query, engine="text-embedding-ada-002")
  df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, query_embedding))
  return df.sort_values("similarity", ascending=False).head(top_n)[["title", "chunk", "similarity"]].to_json()