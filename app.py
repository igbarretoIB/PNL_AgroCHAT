# app.py
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from sentence_transformers import SentenceTransformer, util, models
from langchain.vectorstores import FAISS
from sentence_transformers import SentenceTransformer, models
import os
from PIL import Image
from transformers import logging, BertModel, BertTokenizer
from getpass import getpass
from transformers.hf_api import HfApi
import os
from pathlib import Path
import shutil
import time

logo_menu = Image.open("menu-principal.png")



# def get_pdf_text(pdf_docs):
#     text  = ""
#     for pdf in pdf_docs:
#         pdf_file = pdf
#         pdf_reader = PdfReader(pdf) 
        
#         for page in pdf_reader.pages:
#           text +=  page.extract_text()
#     return text




# def get_pdf_text(pdf_docs):
    
#     text = ""
#     text_chunks = []
    
#     for pdf in pdf_docs:
      
#         pdf_reader = PdfReader(pdf)
        
#         for page_num, page in enumerate(pdf_reader.pages, start=1):
#             page_text = page.extract_text()
            
#             # Adicione o número da página e o nome do PDF ao texto extraído
#             pdf_name = pdf.name
#             text += f"Documento: {pdf_name}, Página: {page_num}\n{page_text}\n\n"

#             # Crie um TextChunk para cada página
#             chunk = TextChunk(len(text_chunks), len(text_chunks) + len(text), text, page_num, pdf_name)
#             text_chunks.append(chunk)

#     return text_chunks



# def get_text_chunks(raw_text):

#     text_splitter = CharacterTextSplitter(
#         separator='\n',  # Fix the typo here
#         chunk_size=1000,
#         chunk_overlap=100,
#         length_function=len
#     )
#     chunks = text_splitter.split_text(raw_text)

#     return chunks



class TextChunk:
    def __init__(self, start_index, end_index, text, page_number, document_name):
        self.start_index = start_index
        self.end_index = end_index
        self.text = text
        self.page_number = page_number
        self.document_name = document_name

class TextProcessor:
    def __init__(self):
        pass

    def get_pdf_text(self, pdf_docs):
        text_chunks = []
        
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                
                # Adicione o número da página e o nome do PDF ao texto extraído
                pdf_name = pdf.name
                text = f"Documento: {pdf_name}, Página: {page_num}\n{page_text}\n\n"
                
                # Crie um TextChunk para cada página
                chunk = TextChunk(len(text_chunks), len(text_chunks) + len(text), text, page_num, pdf_name)
                text_chunks.append(chunk)
        
        return text_chunks

    def get_text_chunks(self, raw_text, page_number, document_name):
        chunks = []
        chunk_size = 1000  # Defina o tamanho do chunk conforme necessário
        
        # Use o CharacterTextSplitter
        text_splitter = CharacterTextSplitter(
            separator='\n',
            chunk_size=chunk_size,
            chunk_overlap=100,  # ajuste conforme necessário
            length_function=len
        )
        
        for chunk_text in text_splitter.split_text(raw_text):
            # Adicione o número da página e o nome do documento ao final de cada chunk
            chunk_text += f"\nDocumento: {document_name}, Página: {page_number}\n"
            
            chunk = TextChunk(len(chunks), len(chunks) + len(chunk_text), chunk_text, page_number, document_name)
            chunks.append(chunk)
        
        return chunks

    def get_text_chunks_from_pdfs(self, pdf_docs):
        all_chunks = []
        
        for pdf_chunk in self.get_pdf_text(pdf_docs):
            raw_text = pdf_chunk.text
            page_number = pdf_chunk.page_number
            document_name = pdf_chunk.document_name
            
            chunks = self.get_text_chunks(raw_text, page_number, document_name)
            
            for chunk in chunks:
                # Atualize o TextChunk com informações adicionais
                chunk.page_number = page_number
                chunk.document_name = document_name
                
            all_chunks.extend(chunks)
        
        return all_chunks

def get_vectorstore(text_chuncks):
    model = SentenceTransformer('neuralmind/bert-base-portuguese-cased')
    embeddings =  HuggingFaceInstructEmbeddings(moodel_name = model)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Desabilita logs desnecessários
logging.set_verbosity_info()

# Se você não estiver autenticado, solicitará suas credenciais
if not HfApi().is_authenticated():
    username = input("Hugging Face Username: ")
    password = getpass("Hugging Face Password: ")
    HfApi().login(username, password)

# Seu nome de usuário no Hugging Face e o nome do repositório
hf_username = "seu-nome-de-usuario"
repo_name = "seu-repositorio"

def main():
    load_dotenv() ## Ler as credenciais do huggingface armazenadas no diretorio .env
    st.set_page_config(page_title= 'AgroCHAT', page_icon =':male-farmer:')
    st.header('AgroCHAT :male-farmer:')
    
    

    


    prompt = st.chat_input('Digite algo') 
    
    
    with st.sidebar:
        col1, col2 = st.columns([1, 20])

        with col1:
            st.image('8212733.png', width=40)


        with col2:
              st.markdown("<p style='margin-top: 3px; margin-bottom: 10px; margin-left: 10px;text-align: left; font-size: 20px; font-weight: bold;'>Menu</p>", unsafe_allow_html=True)

        
        
       
        pdf_docs= st.file_uploader("Faça o Upload dos seus PDFs aqui e clique em 'Process' ", accept_multiple_files= True)
        
        # if st.button("Process"):
        #     with st.spinner('Processing'):    
        #         # Extrair o texto do pdf
        #         raw_text = get_pdf_text(pdf_docs)
            
        #         # Extrair os text chunks 
        #         text_chunks = get_text_chunks(raw_text)
        #         st.write(text_chunks)
            
  
        #         pass
        st.subheader("Refências :bookmark_tabs:")
        if st.button("Process"):
            with st.spinner('Processing'):
                text_processor = TextProcessor()
                
                # Extrair os text chunks dos documentos PDF
                text_chunks = text_processor.get_text_chunks_from_pdfs(pdf_docs)

                # Iterar sobre os chunks para mostrar as informações
                for chunk in text_chunks:
                    st.write(f"Chunk {chunk.start_index} to {chunk.end_index}")
                    st.write(f"Document Name: {chunk.document_name} Page Number: {chunk.page_number}")
                    st.write(chunk.text)
                    st.write("\n")


   
            pass
            
                        
    
    time.sleep(2)
    with st.chat_message("assistant"):
        st.write("Olá, como posso ajudar!")
        pass
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
    
    if prompt:
        with st.chat_message("assistant"):
            st.write(prompt)
            pass  # Substitua pelo seu código real
if __name__ == "__main__":
    main()
