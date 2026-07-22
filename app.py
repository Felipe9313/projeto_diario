import json
import base64
import pdfplumber
import streamlit as st
import vertexai
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

# 1. Busca a chave correta que você acabou de configurar no Secrets
b64_string = st.secrets["SERVICE_ACCOUNT_B64"]

# 2. Decodifica a string para o formato JSON correto
json_bytes = base64.b64decode(b64_string)
service_account_info = json.loads(json_bytes)

# 3. Cria as credenciais com o JSON limpo
credentials = service_account.Credentials.from_service_account_info(service_account_info)

# 4. Inicializa o Vertex AI
vertexai.init(
    project=service_account_info["project_id"], 
    location="southamerica-east1", 
    credentials=credentials
)

model = GenerativeModel("gemini-1.5-flash")

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

            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")

