import streamlit as st
import pdfplumber
import pandas as pd
import google.generativeai as genai
import os

# Configuração da página
st.set_page_config(page_title="Monitor de Diários - São Carlos", layout="wide")

st.title("🛡️ Monitor do Diário Oficial")
st.markdown("Faça o upload do PDF e deixe a IA organizar as movimentações para você.")

# Configuração da API (O Streamlit usa o 'st.secrets' para segurança)
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-flash-lite-latest')

# Interface
uploaded_file = st.file_uploader("Selecione o PDF do Diário", type="pdf")

if uploaded_file:
    with st.spinner('Lendo PDF e processando com IA...'):
        # Leitura
        texto_extraido = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                texto_extraido += page.extract_text() or ""
        
        # Análise
        prompt = f"Extraia movimentações de servidores do texto abaixo em formato de tabela Markdown: {texto_extraido[:12000]}"
        response = model.generate_content(prompt)
        
        # Exibição
        st.subheader("Resultados")
        st.markdown(response.text)
        
        st.success("Análise concluída!")