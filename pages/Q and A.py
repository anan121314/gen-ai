import os
import pdfplumber
from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams
import pandas as pd
import docx2txt
import streamlit as st
import chromadb
from chromadb.config import Settings

creds = Credentials("pak-4D7V0iz9n86tsi2BH48ezpshf0mmxTnnPnvHl2dJatw", api_endpoint="https://bam-api.res.ibm.com/v1")

def generateparams(decoding,token,temp,model,creds):
    model_param=GenerateParams(decoding_method=decoding, max_new_tokens=token, temperature=temp)
    output = Model(model, params=model_param, credentials=creds)
    print(model,model_param)
    return output
#alice = Model("meta-llama/llama-2-70b-chat", params=alice_params, credentials=creds)
#alice = Model("google/flan-ul2", params=alice_params, credentials=creds)

# current_directory = os.getcwd()
# client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",persist_directory=f"{current_directory}/collection"))
# collection=client.get_collection("my_collection")


def make_prompt(instruction, context, question_text):
   return (f"""{instruction}\n"""
          + f"Information :\n{context}.\n"
          + f"{question_text}?\n")

def process_text(text):
    if text.strip():
        results = collection.query(
        query_texts=[query],
        n_results=3
)
    return results

def generate_answer(alice,instruction,relevant,text):
    context = '. '.join(relevant)
    prompt_text = make_prompt(instruction,context, text)
    lines=prompt_text
    print(lines)
    alice_response = alice.generate([lines])
    alice_gen = alice_response[0].generated_text
    print(f"Watson : \n{alice_gen}")
    return alice_gen

model_options=['meta-llama/llama-2-70b-chat','google/flan-ul2',]
model=st.selectbox('Select model:', model_options)
options = ['sample', 'greedy']
decoding = st.selectbox('Select decoding:', options)
token=st.number_input('Enter maximum token:', min_value=10, step=1,value=100)
temp=st.slider('Select temperature:', min_value=0.001, max_value=1.0001,step=0.1, value=0.2)
alice=generateparams(decoding,token,temp,model,creds)
instruction=st.text_area("Enter instruction here", "")
query=st.text_input("Enter your query.")
if query:
    current_directory = os.getcwd()
    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",persist_directory=f"{current_directory}/collection"))
    collection=client.get_collection("my_collection")
    result=process_text(query)
    relevant_texts=result["documents"][0]
    sources=result["metadatas"][0]
    answer=generate_answer(alice,instruction,relevant_texts,query)
    st.write(answer)
    st.info('Below are the relevant portions of document from which the answer is generated. Expand each to view the relevant portions.')
    k=0
    for i in relevant_texts:

        with st.expander(f"Source : {sources[k]['source']}, Title: {sources[k]['title']}"):
            st.write(i)
        k=k+1
    k=0    
