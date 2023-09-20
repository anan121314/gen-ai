import os
import pdfplumber
from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams
import pandas as pd
import docx2txt
import streamlit as st

#API credentials for bam.res
creds = Credentials("pak-4D7V0iz9n86tsi2BH48ezpshf0mmxTnnPnvHl2dJatw", api_endpoint="https://bam-api.res.ibm.com/v1")

#Initialising model 1
alice_params = GenerateParams(decoding_method="greedy", max_new_tokens=250, temperature=0.1)
alice = Model("meta-llama/llama-2-70b-chat", params=alice_params, credentials=creds)

#Initialising model 2
binary_params = GenerateParams(decoding_method="greedy", max_new_tokens=3, temperature=0.1)
binary = Model("google/flan-ul2", params=binary_params, credentials=creds)

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

def make_prompt_binary(context,params):
   return (f"""Identify weather the information given below contains data related to {params}. Answer yes or no only. Give yes if any of the data related to {params} are present else give no. No explanation is needed. Just say yes or no\n"""
          + f"Information :\n{context}.\n\n")
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
def count_occurence(chunks,params):
    occurence_list=[]
    for i in chunks:
        prompt_text_binary=make_prompt_binary(i,params)
        print(prompt_text_binary)
        binary_response = binary.generate([prompt_text_binary])   
        binary_gen = binary_response[0].generated_text
        occurence_list.append(binary_gen)
        print(binary_gen)
    yes_count=occurence_list.count('yes')
    total_count=len(occurence_list)
    percent_match=round((yes_count/total_count)*100,2)
    return percent_match


def copy_file_default(percent_match,file):
    if file is not None:
        file_name=file.name
        try:
            if percent_match>=75:
                os.makedirs("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_75-100%\\", exist_ok=True)
                destination_path = os.path.join("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_75-100%\\", file_name)
            elif percent_match < 75 and percent_match >= 50:
                os.makedirs("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_50-75%\\", exist_ok=True)
                destination_path = os.path.join("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_50-75%\\", file_name)
            elif percent_match < 50 and percent_match >= 25:
                os.makedirs("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_25-50%\\", exist_ok=True)
                destination_path = os.path.join("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_25-50%\\", file_name)
            elif percent_match < 25 and percent_match >= 10:
                os.makedirs("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_10-25%\\", exist_ok=True)
                destination_path = os.path.join("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_10-25%\\", file_name)
            else:
                os.makedirs("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_0-10%\\", exist_ok=True)
                destination_path = os.path.join("C:\\Users\\002H26744\\Desktop\\relevant_files\\relevant_0-10%\\", file_name)
 
            # Copy the file to the destination
            with open(destination_path, "wb") as f:
                f.write(file.read())
            
            st.success(f"File '{file_name}' has been copied to '{destination_path}'.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def copy_file_custom(file_path,file):
    try:
        file_name=file.name
        os.makedirs(file_path, exist_ok=True)
        destination_path = os.path.join(file_path, file_name)
        with open(destination_path, "wb") as f:
                    f.write(file.read())
        st.success(f"File '{file_name}' has been copied to '{destination_path}'.")
    except Exception as e:
            st.error(f"An error occurred: {e}")            

uploaded_file = st.file_uploader("Choose a file...", type=["xlsx","docx", "txt", "csv", "pdf"],key="file_uploader")
# Check if a file has been uploaded
if uploaded_file is not None:
    # Display the file details (name, size, type)
    file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    text=to_text(uploaded_file,uploaded_file.name)
    text_formatted = text.replace('\n', ' ')
    chunks=get_overlapped_chunks(text_formatted, 1000, 300)

st.markdown(
"""
<style>
.stTextInput {
    margin-left:-1px;
    width:100%;
    color: #333;
    padding: 0px;
    font-size: 16px;
}
</style>
""",
unsafe_allow_html=True,
)
# Create a text input field
user_input = st.text_input("Enter the relevant parameters seperated by comma")
user_input = user_input.replace(',', ', ')

last_comma_index = user_input.rfind(',')

if last_comma_index != -1:
    # Replace the last comma with 'or'
    new_string = user_input[:last_comma_index] + ' or' + user_input[last_comma_index + 1:]
else:
    new_string = user_input

params=new_string

selected_option = st.radio("Select classification criteria: (If default the file will be classified and moved to corresponding folders in desktop)", ["Default", "Custom"])

if selected_option=='Custom':
    custon_percent=st.text_input("Enter desired acceptance percentage",key='percen')
    custom_path=st.text_input("Enter destination path",key='path')


#Button to check relevancy
if st.button("Check Relevancy"):
    percentage=int(count_occurence(chunks,params))
    st.progress(percentage)  
    st.info(f"The document is {percentage}% relevant")
    if selected_option=='Default':
        copy_file_default(percentage,uploaded_file)
    elif selected_option=='Custom':    
        if percentage>=int(custon_percent):
            copy_file_custom(custom_path,uploaded_file)
        else:
            st.warning("Document did not meet acceptance criteria")
        
  
st.sidebar.header('')