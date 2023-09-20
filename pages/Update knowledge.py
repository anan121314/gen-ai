from asyncio import Server
import chromadb
from chromadb.config import Settings
import uuid
import streamlit as st
import pdfplumber
import docx2txt
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

def refresh():
    Server.get_current()._reloader.reload()


client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                    persist_directory="C:/Users/002H26744/Desktop/collection"
                                ))

collection=client.get_collection("my_collection")

#Extracting text functions
def extract_text_from_excel(file_path):
    text = ""
    text = pd.read_excel(file_path).to_csv(index=False, sep=' ')
    return text

def extract_text_from_docx(file_path):
    text=''
    text = docx2txt.process(file_path)
    return text

def extract_text_from_csv(file_path):
    text = ""
    text = pd.read_csv(file_path).to_csv(index=False, sep=' ')
    return text

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_text_from_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        return str(e)
def get_overlapped_chunks(textin, chunksize, overlapsize):  
    return [textin[a:a+chunksize] for a in range(0,len(textin), chunksize-overlapsize)]    

def to_text(file_name,name):
    file_extension = name.split('.')[-1].lower()
    if file_extension == 'xlsx':
        return extract_text_from_excel(file_name)
    elif file_extension == 'csv':
        return extract_text_from_csv(file_name)
    elif file_extension == 'txt':
        return extract_text_from_text(file_name)
    elif file_extension == 'docx':
        return extract_text_from_docx(file_name)
    elif file_extension == 'pdf':
        return extract_text_from_pdf(file_name)
    else:
        print('Unknown File Type')


def generate_unique_id():
    return str(uuid.uuid4())


def insert_data(doc_data,source,title):
    collection.add(
    ids=generate_unique_id(),
    documents=[doc_data],
    metadatas=[{"source":source,"title":title}],)
    client.persist()

def update_from_doc(data,input_source,input_title):
    for i in data:
        collection.add(
        ids=generate_unique_id(),
        documents=[i],
        metadatas=[{"source":input_source,"title":input_title}],)
    client.persist() 

selected_option = st.radio("Select Data entry method", ["Enter data in the form of text", "Enter data from file"])
if selected_option=='Enter data in the form of text':
    doc_data=st.text_input('Enter the text data.')  
    if doc_data.strip():
        source=st.text_input('Enter source of the data.')  
        title=st.text_input('Enter title of the data.')  
        if st.button('Enter data'):
            insert_data(doc_data,source,title)
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
            #st.write(collection.get()['documents'])
elif selected_option=="Enter data from file":
    uploaded_file = st.file_uploader("Choose a file...", type=["xlsx","docx", "txt", "csv", "pdf"],key="file_uploader")
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Display the file details (name, size, type)
        file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        source_file=st.text_input('Enter source of the file.')  
        title_file=st.text_input('Enter title of the file.') 
        text=to_text(uploaded_file,uploaded_file.name)
        chunks=get_overlapped_chunks(text, 1000, 300)
        if st.button('Upload data'):
            update_from_doc(chunks,source_file,title_file)
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
        #st.write(collection.get()["documents"])    