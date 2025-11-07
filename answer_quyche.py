import os
import json
from sklearn.metrics.pairwise import cosine_similarity
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from uuid import uuid4
from langchain_core.documents import Document
from tiktoken import encoding_for_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts.prompt import PromptTemplate
import time

pc = Pinecone(api_key='')

index_name = '251107-data-retrieval-bk-quyche'
index = pc.Index(index_name)
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)
retriever = vector_store.as_retriever(search_kwargs={'k': 5})
prompt = PromptTemplate(
    input_variables=["context", "question", "answer"],
    template="""
Bạn là trợ lý ảo của Đại học Bách khoa Hà Nội.
Dựa vào các đoạn văn sau đây, hãy chọn ra câu trả lời đúng nhất từ các câu trả lời dưới đây, chỉ dựa vào thông tin trong văn bản.
LƯU Ý: chỉ trả về NGUYÊN VĂN câu trả lời bạn chọn, không giải thích gì thêm, không trả về các câu trả lời khác.

Context:
{context}

Câu hỏi:
{question}

Các câu trả lời:
{answer}

Câu trả lời đúng nhất:
""")

question_count = 0
correct_avg_count = 0
correct_max_count = 0
process_data = []
with open('quyche.json', 'r', encoding='utf-8') as f:
  questions = json.load(f)
  for question in questions:
    results = vector_store.similarity_search(question['question'], k=5)
    avg_cosine_score = 0
    max_cosine_score = 0
    system_answer_avg = ''
    system_answer_max = ''

    vec_results = []
    for result in results:
      vec_results.append(embeddings.embed_query(result.page_content))

    for answer in question['answer']:
      max_score = 0
      avg_score = 0
      for vec_result in vec_results:
        vec_answer = embeddings.embed_query(answer)
        score = cosine_similarity([vec_answer], [vec_result])[0][0]
        if score > max_score:
          max_score = score
        avg_score += score / 5
     
      print(answer, max_score, avg_score)
      if max_score > max_cosine_score:
        max_cosine_score = max_score
        system_answer_max = answer
      if avg_score > avg_cosine_score:
        avg_cosine_score = avg_score
        system_answer_avg = answer

    truth_answer = question.get('correctAnswer', '')
    print('Truth answer:', truth_answer)
    print('System answer avg:', system_answer_avg)
    print('System answer max:', system_answer_max)

    context = "\n\n".join([doc.page_content for doc in results])
    answers_text = "\n".join(question['answer'])

    prompt_text = prompt.format(
        context=context,
        question=question['question'],
        answer=answers_text
    )

    llm_response = llm.invoke(prompt_text)
    print("Gemini trả lời:", llm_response.content)


    if system_answer_avg == truth_answer:
      correct_avg_count += 1
    if system_answer_max == truth_answer:
      correct_max_count += 1
    question_count += 1
    process_data.append({
      'question': question['question'],
      'truth_answer': truth_answer,
      'system_answer_avg': system_answer_avg,
      'system_answer_max': system_answer_max,
      'system_answer_llm': llm_response.content
    })
    time.sleep(20)

  print(f'Correct avg count: {correct_avg_count}')
  print(f'Correct max count: {correct_max_count}')
  print(f'Question count: {question_count}')

with open('process_data.json', 'w', encoding='utf-8') as f:
  json.dump(process_data, f, ensure_ascii=False, indent=2)