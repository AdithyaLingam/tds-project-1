# # app/rag_pipeline.py
# import chromadb
# import os
# from openai import OpenAI
# from .config import settings
# from .models import Link
# from dotenv import load_dotenv
# from chromadb.errors import NotFoundError

# # Initialize clients once to be reused
# load_dotenv()

# openai_client = os.getenv("OPENAI_API_KEY")
# chroma_client = chromadb.PersistentClient(path=str(settings.VECTOR_STORE_DIR))
# try:
#     collection = chroma_client.get_collection(name="tds_virtual_ta")
# except NotFoundError:
#     collection = chroma_client.create_collection(name="tds_virtual_ta")


# def embed_function(texts):
#     response = openai_client.embeddings.create(
#         input=texts,
#         model=settings.EMBEDDING_MODEL
#     )
#     return [r.embedding for r in response.data]


# def query_and_generate(question: str) -> (str, list[Link]):
#     """
#     Queries the vector store and generates an answer using an LLM.
#     """
#     # 1. Query ChromaDB to find relevant context
#     query_embedding = embed_function([question])[0]
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=5 # Get the top 5 most relevant documents
#     )
    
#     context_docs = results['documents'][0]
#     metadatas = results['metadatas'][0]
    
#     if not context_docs:
#         return "I could not find any relevant information in my knowledge base to answer your question.", []
        
#     # 2. Build the prompt for the LLM
#     context = "\n---\n".join(
#         [f"Source: {meta['source']}\nContent: {doc}" for doc, meta in zip(context_docs, metadatas)]
#     )
    
#     system_prompt = """
#     You are a helpful Teaching Assistant for the IIT Madras 'Tools in Data Science' course.
#     Your task is to answer a student's question based *only* on the provided context from the course's Discourse forum.
#     - Be direct and concise.
#     - If the context does not contain the answer, state that you don't have enough information.
#     - Synthesize information from multiple sources if necessary.
#     - For each piece of information in your answer, reference the source URL from the context.
#     - Your final output must be a single JSON object with two keys: "answer" (a string) and "links" (a list of JSON objects, each with "url" and "text" keys).
#     - The "text" in the links should be a direct, relevant quote from the source.
#     """
    
#     user_prompt = f"""
#     CONTEXT:
#     ---
#     {context}
#     ---
#     STUDENT'S QUESTION: {question}
#     """
    
#     # 3. Call the LLM to generate the answer
#     # Using the JSON response format feature of new OpenAI models
#     response = openai_client.chat.completions.create(
#         model=settings.LLM_MODEL,
#         response_format={"type": "json_object"},
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ]
#     )
    
#     return response.choices[0].message.content


# app/rag_pipeline.py
import requests
from app.config import settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings, OllamaEmbeddings
from langchain_community.llms import OpenAI, Ollama
from langchain.chains import RetrievalQA

def load_vector_store():
    embeddings = (
        OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        if settings.USE_OPENAI else
        OllamaEmbeddings(model="nomic-embed-text")
    )
    return Chroma(
        persist_directory=str(settings.VECTOR_STORE_DIR),
        embedding_function=embeddings
    )

def get_rag_chain():
    retriever = load_vector_store().as_retriever()
    llm = (
        OpenAI(model=settings.LLM_MODEL, temperature=0, openai_api_key=settings.OPENAI_API_KEY)
        if settings.USE_OPENAI else
        Ollama(model=settings.LLM_MODEL)
    )
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

def query_and_generate(query: str) -> str:
    if settings.USE_OPENAI:
        chain = get_rag_chain()
        return chain.run(query)
    else:
        return query_openwebui(query)

def query_openwebui(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": settings.LLM_MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        return res.json()["response"]
    except Exception as e:
        return f"Error querying OpenWebUI: {e}"
