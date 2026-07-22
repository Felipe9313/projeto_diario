import base64
import json
import pandas as pd
import pdfplumber
import streamlit as st
import vertexai

from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

# -------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------

st.set_page_config(
    page_title="Analisador de Diário Oficial",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Analisador de Diário Oficial")
st.write("Extração automática de movimentações de servidores públicos utilizando Gemini.")

# -------------------------------
# AUTENTICAÇÃO
# -------------------------------

try:
    b64_string = st.secrets["SERVICE_ACCOUNT_B64"]

    json_bytes = base64.b64decode(b64_string)
    service_account_info = json.loads(json_bytes)

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info
    )

    vertexai.init(
        project=service_account_info["project_id"],
        location="us-central1",
        credentials=credentials
    )

    model = GenerativeModel("gemini-2.5-flash")

except Exception as e:
    st.error(f"Erro ao conectar ao Vertex AI:\n\n{e}")
    st.stop()

# -------------------------------
# UPLOAD
# -------------------------------

uploaded_file = st.file_uploader(
    "Selecione um Diário Oficial (PDF)",
    type="pdf"
)

if uploaded_file:

    with st.spinner("Lendo PDF..."):

        try:

            texto = ""

            with pdfplumber.open(uploaded_file) as pdf:

                for pagina in pdf.pages:

                    texto += pagina.extract_text() or ""
                    texto += "\n"

            if texto.strip() == "":
                st.error("Não foi possível extrair texto do PDF.")
                st.stop()

        except Exception as e:
            st.error(f"Erro ao ler o PDF:\n\n{e}")
            st.stop()

    with st.spinner("Analisando com Gemini..."):

        try:

            prompt = f"""
Você é especialista em Diários Oficiais brasileiros.

Analise o texto abaixo e encontre SOMENTE atos relacionados a servidores públicos.

Considere:

- Nomeação
- Exoneração
- Transferência
- Remoção
- Designação
- Promoção
- Posse
- Licença
- Afastamento
- Cessão

Retorne SOMENTE um JSON válido.

Formato:

[
  {{
    "nome":"",
    "matricula":"",
    "cargo":"",
    "secretaria":"",
    "tipo_ato":"",
    "data":""
  }}
]

Regras:

- Nunca invente dados.
- Se não existir matrícula escreva "N/I".
- Se não existir cargo escreva "N/I".
- Se não existir secretaria escreva "N/I".
- Se não existir data escreva "N/I".
- Não utilize Markdown.
- Não escreva explicações.
- Retorne apenas o JSON.

Texto:

{texto[:120000]}
"""

            response = model.generate_content(prompt)

            resposta = response.text.strip()

            resposta = resposta.replace("```json", "")
            resposta = resposta.replace("```", "")
            resposta = resposta.strip()

            dados = json.loads(resposta)

            df = pd.DataFrame(dados)

            st.success(f"{len(df)} movimentações encontradas.")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            csv = df.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                "⬇️ Baixar CSV",
                csv,
                file_name="movimentacoes.csv",
                mime="text/csv"
            )

        except json.JSONDecodeError:

            st.error("O Gemini retornou uma resposta que não é um JSON válido.")
            st.code(response.text)

        except Exception as e:

            st.error(f"Erro durante a análise:\n\n{e}")