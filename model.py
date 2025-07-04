import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import google.generativeai as genai

def load_model(text):
    load_dotenv()  
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Google API key not found in .env file")

    genai.configure(api_key=api_key)
    # text = ""
    # with open(file_path, 'r') as file:
    #     text = file.read()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    return vector_store

def get_response(vector_store, question_text):
    docs = vector_store.similarity_search(question_text)
    prompt_template = '''
        Context:\n {context}\n
        Question: {question}\n

        based on the context answer the question with an interactive way in 5 lines,
        if the answer is lenthy ask them the topic keep the constraint that it should be in five lines,
        if the question is not related to the context say 'no answer available dont give me in points explain it in a paragraph'
    '''
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    resp = chain({"input_documents": docs, "question": question_text}, return_only_outputs=True)
    return resp['output_text'].replace('*', '') 
