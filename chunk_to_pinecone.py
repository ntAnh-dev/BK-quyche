import os
import json

from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from uuid import uuid4
from langchain_core.documents import Document
from tiktoken import encoding_for_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer

pc = Pinecone(api_key='')

index_name = '251107-data-retrieval-bk-quyche'
if not pc.has_index(index_name):
  pc.create_index(
    name=index_name,
    dimension=1024,
    metric='cosine',
    spec=ServerlessSpec(cloud='aws', region='us-east-1')
  )

index = pc.Index(index_name)
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

with open('chunks.json', 'r', encoding='utf-8') as f:
  chunks = json.load(f)
  for chunk in chunks:
    vector_store.add_documents(documents=[Document(page_content=chunk['content'], metadata={ 'file': chunk['file'] })])