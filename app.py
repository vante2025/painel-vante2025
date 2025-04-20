
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

if "pagina" not in st.session_state:
    st.session_state.pagina = "tabela"
if "site" not in st.session_state:
    st.session_state.site = ""
if "projeto" not in st.session_state:
    st.session_state.projeto = ""
if "filtro_status" not in st.session_state:
    st.session_state.filtro_status = None

@st.cache_data
def carregar_dados():
    df = pd.read_excel("Status Sites.xlsx", sheet_name="Controle")
    df = df.dropna(subset=["ID Winity", "Candidato"])
    df = df[df["Candidato"].isin(["A", "B", "C", "D"])]
    df = df.fillna("")
    return df

def exibir_logo_projeto(nome_projeto):
    caminho_logo = f"logo_{nome_projeto.lower().replace(' ', '_')}.png"
    try:
        st.image(caminho_logo, width=120)
    except:
        pass

def indicadores(df_proj):
    etapas = {
        "VOADO": "VOO",
        "PROCESSAMENTO VOO": "Processamento Voo",
        "SAR": "SAR",
        "QUALIFICADO": "Validação Aquisição",
        "QUALIFICADO OPERADORA": "SAR QUALIFICADO OPERADORA",
        "QUALIFICADO CONCESSIONÁRIA": "Analise Concessionária",
        "KIT ELABORADO": "KIT ELABORADO",
        "KIT APROVADO": "KIT APROVADO",
        "EM ANÁLISE AGÊNCIA": "EM ANÁLISE AGÊNCIA",
        "PUBLICAÇÃO DO": "PUBLICAÇÃO DIÁRIO",
        "EMISSÃO CPEU": "CPEU"
    }

    colunas = st.columns(len(etapas) + 1)
    colunas[0].markdown("### 🗼 TOTAL DE SITES")
    colunas[0].markdown(f"<h2 style='color:green'>{df_proj['ID Winity'].nunique()}</h2>", unsafe_allow_html=True)

    for i, (etapa, coluna) in enumerate(etapas.items()):
        if coluna not in df_proj.columns:
            valor = "N/A"
        else:
            valor = df_proj[coluna].astype(str).str.len().gt(0).sum()
        if st.button(etapa, key=f"filtro_{etapa}"):
            st.session_state.filtro_status = etapa if st.session_state.filtro_status != etapa else None
        colunas[i+1].markdown(f"<h3 style='color:#1E90FF'>{valor}</h3>", unsafe_allow_html=True)

def pagina_tabela():
    df = carregar_dados()

    st.image("logo_vante.png", width=140)
    projetos = st.multiselect("Selecione o Projeto:", sorted(df["Projeto"].dropna().unique()))
    if not projetos:
        return

    df_proj = df[df["Projeto"].isin(projetos)]

    indicadores(df_proj)

    df_vigente = df_proj.copy()
    df_vigente["Rev_int"] = pd.to_numeric(df_vigente["Revisão"], errors="coerce").fillna(0).astype(int)
    df_vigente.sort_values(by=["ID Winity", "Candidato", "Rev_int"], ascending=[True, True, False], inplace=True)
    df_vigente["Status_lower"] = df_vigente["STATUS"].str.lower()

    df_filtrado = (
        df_vigente[df_vigente["Status_lower"].isin(["qualificado", "em qualificação"])]
        .drop_duplicates(subset="ID Winity", keep="first")
    )

    # Se não houver nenhum qualificado/em qualificação, pega o de maior revisão
    restante = df_vigente[~df_vigente["ID Winity"].isin(df_filtrado["ID Winity"])]
    df_restante = restante.drop_duplicates(subset="ID Winity", keep="first")

    df_final = pd.concat([df_filtrado, df_restante]).drop_duplicates(subset="ID Winity", keep="first")

    if st.session_state.filtro_status:
        etapa_coluna = {
            "VOADO": "VOO",
            "PROCESSAMENTO VOO": "Processamento Voo",
            "SAR": "SAR",
            "QUALIFICADO": "Validação Aquisição",
            "QUALIFICADO OPERADORA": "SAR QUALIFICADO OPERADORA",
            "QUALIFICADO CONCESSIONÁRIA": "Analise Concessionária",
            "KIT ELABORADO": "KIT ELABORADO",
            "KIT APROVADO": "KIT APROVADO",
            "EM ANÁLISE AGÊNCIA": "EM ANÁLISE AGÊNCIA",
            "PUBLICAÇÃO DO": "PUBLICAÇÃO DIÁRIO",
            "EMISSÃO CPEU": "CPEU"
        }
        filtro_coluna = etapa_coluna[st.session_state.filtro_status]
        df_final = df_final[df_final[filtro_coluna].astype(str).str.len() > 0]

    df_final["Ver Detalhes"] = df_final["ID Winity"].apply(lambda x: f"🔎 {x}")
    colunas_exibir = ["ID Winity", "ID Operadora", "Candidato", "Revisão", "Altura da Torre Final (m)",
                      "Município", "UF", "Rodovia", "KM", "Latitude Candidato", "Longitude Candidato", "STATUS"]
    st.dataframe(df_final[colunas_exibir], use_container_width=True, hide_index=True)

    site_escolhido = st.selectbox("Selecione um site para detalhes:", df_final["ID Winity"].unique())
    if st.button("Ver detalhes"):
        st.session_state.site = site_escolhido
        st.session_state.pagina = "detalhe"
        st.rerun()

def pagina_detalhe():
    st.write("Detalhamento do site (em construção).")
    if st.button("Voltar"):
        st.session_state.pagina = "tabela"
        st.rerun()

if st.session_state.pagina == "tabela":
    pagina_tabela()
else:
    pagina_detalhe()
