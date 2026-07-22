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
Você é um especialista em Diários Oficiais brasileiros.

Sua função é identificar APENAS movimentações funcionais de servidores públicos.

Considere SOMENTE os seguintes atos:

- Nomeação
- Exoneração
- Contratação (temporária, CLT, processo seletivo, concurso, admissão)

IGNORE COMPLETAMENTE qualquer outro tipo de ato, incluindo:

- Designação de gestor de contrato
- Designação de fiscal de contrato
- Designação para comissão
- Designação de comissão de licitação
- Comissão de sindicância
- Comissão de processo administrativo
- Nomeação de comissão
- Substituição de gestor
- Delegação de competência
- Portarias administrativas
- Convênios
- Licitações
- Contratos
- Aditivos
- Compras públicas
- Autorizações
- Homologações
- Ratificações
- Atos financeiros

IMPORTANTE:

Mesmo que apareçam nome, cargo e matrícula de servidores, NÃO retorne esses registros se o ato não for uma Nomeação, Exoneração ou Contratação.

Retorne apenas registros cuja situação funcional do servidor tenha sido alterada.

Retorne somente um JSON válido.

Formato:

[
  {
    "nome":"",
    "matricula":"",
    "cargo":"",
    "secretaria":"",
    "tipo_ato":"",
    "data":""
  }
]

Se não existir nenhuma Nomeação, Exoneração ou Contratação, retorne:

[]

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
