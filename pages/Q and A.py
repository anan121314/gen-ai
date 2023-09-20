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

alice_params = GenerateParams(decoding_method="greedy", max_new_tokens=250, temperature=0.1)
alice = Model("meta-llama/llama-2-70b-chat", params=alice_params, credentials=creds)

client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                    persist_directory="/content/"
                                ))

collection=client.get_collection("my_information")

def make_prompt(context, question_text):
   return (f"""Strictly follow the instructions below
               1. Provide an answer based only on the information provided.
               2. If the answer is not in the information provided reply "No information available".
               3. For answer containing list of items. Reply as bullet points.
               4. Do not add any text mentionin "information provided" in the answer text.\n"""
          + f"Information :\n{context}.\n\n"
          + f"{question_text}?\n")

def process_text(text):
    if text.strip():
        results = collection.query(
        query_texts=[query],
        n_results=3
)
    return results

def generate_answer(relevant,text):
    context = '. '.join(relevant)
    prompt_text = make_prompt(context, text)
    lines=prompt_text.replace('/n','. ')
    alice_response = alice.generate([lines])   
    alice_gen = alice_response[0].generated_text
    print(f"Watson : \n{alice_gen}")
    return alice_gen

query=st.text_input("Enter your query.")
if query:
    result=process_text(query)
    relevant_texts=result["documents"][0]
    sources=result["metadatas"][0]
    answer=generate_answer(relevant_texts,query)
    st.write(answer)
    st.info('Below are the relevant portions of document from which the answer is generated. Expand each to view the relevant portions.')
    k=0
    for i in relevant_texts:

        with st.expander(f"Source : {sources[k]['source']}, Title: {sources[k]['title']}"):
            st.write(i)
        k=k+1
    k=0    
