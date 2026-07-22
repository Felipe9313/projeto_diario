import streamlit as st

import json
import os
import vertexai
import pdfplumber  # <--- ADICIONE ESTA LINHA AQUI
from vertexai.generative_models import GenerativeModel

import pdfplumber
import google.generativeai as genai


# 1. Carrega as credenciais que configuramos nos Secrets
# Importante: O nome "SERVICE_ACCOUNT_JSON" aqui tem que ser IGUAL ao que você digitou no painel do Streamlit
service_account_info = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])

# 2. Grava essas credenciais em um arquivo temporário para o Google ler
with open("temp_creds.json", "w") as f:
    json.dump(service_account_info, f)


# 3. Configura a variável de ambiente para usar esse arquivo
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_creds.json"

# 4. Inicializa o Vertex AI
vertexai.init(project=service_account_info["project_id"], location="us-central1")
model = GenerativeModel("gemini-1.5-flash")

# ... (o resto do seu código continua aqui embaixo normalmente)

=======
# Configuração da chave de API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-flash-lite-latest')
else:
    st.error("Erro: A chave GOOGLE_API_KEY não foi encontrada nos Segredos (Secrets) do Streamlit.")
    st.stop()


# Interface de upload
uploaded_file = st.file_uploader("Selecione o PDF do Diário", type="pdf")

if uploaded_file:
    with st.spinner('Lendo o PDF e analisando com IA...'):
        try:
            # 1. Leitura do PDF
            texto_extraido = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    texto_extraido += page.extract_text() or ""
            
            if not texto_extraido:
                st.warning("Não foi possível extrair texto deste PDF. Verifique se ele é uma imagem ou um arquivo corrompido.")
                st.stop()

            # 2. Limpeza de caracteres especiais
            texto_limpo = "".join([c if ord(c) < 128 else " " for c in texto_extraido])
            
            # 3. Prompt de análise
            prompt = f"""
            Você é um especialista em análise de Diários Oficiais.
            Analise o texto abaixo e extraia todas as movimentações de servidores (nomeações, exonerações, transferências, etc).
            Retorne APENAS uma tabela Markdown com as colunas: | Nome | Matrícula | Secretaria | Cargo | Tipo de Ato | Data |.
            Se não encontrar uma informação específica para um campo, escreva 'N/I'.
            
            Texto:
            {texto_limpo[:10000]}
            """
            
            # 4. Chamada à API
            response = model.generate_content(prompt)
            
            # 5. Exibição dos resultados
            st.subheader("Resultados da Extração")
            st.markdown(response.text)
            st.success("Análise concluída com sucesso!")
            
        except Exception as e:

            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
=======
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")

