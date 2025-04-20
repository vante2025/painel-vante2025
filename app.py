
import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

if "pagina" not in st.session_state:
    st.session_state.pagina = "tabela"

@st.cache_data
def carregar_dados():
    arquivos = os.listdir(".")
    planilha = next((f for f in arquivos if f.lower().endswith(".xlsx") and "status" in f.lower()), None)
    if not planilha:
        st.error("Arquivo da planilha não encontrado no diretório. Verifique se o arquivo .xlsx está corretamente nomeado.")
        st.stop()
    df = pd.read_excel(planilha, sheet_name="Planilha1")
    return df.fillna("")

def indicadores(df):
    etapas = {
        "VOADO": "Data Voo",
        "PROCESSAMENTO VOO": "Processamento",
        "SAR": "SAR",
        "QUALIFICADO": "Qualificação",
        "QUALIFICADO OPERADORA": "Qualificação Operadora",
        "QUALIFICADO CONCESSIONÁRIA": "Qualificação Concessionária",
        "KIT ELABORADO": "Kit",
        "KIT APROVADO": "Aprovação Concessionária",
        "EM ANÁLISE AGÊNCIA": "Análise Agência",
        "PUBLICAÇÃO DO": "Publicação DO",
        "EMISSÃO CPEU": "Emissão CPEU"
    }
    col1, col2 = st.columns([3, 1])
    with col1:
        for etapa, coluna in etapas.items():
            total = df[coluna].astype(str).str.len().gt(0).sum()
            st.metric(label=etapa, value=total)
    with col2:
        st.metric("TOTAL DE SITES", df["ID Winity"].nunique())

def pagina_tabela():
    st.image("logo_vante.png", width=160)
    df = carregar_dados()

    projetos = df["Projeto"].unique()
    projetos_sel = st.multiselect("Selecione o Projeto:", projetos, default=projetos[:1])
    df_proj = df[df["Projeto"].isin(projetos_sel)]

    if not df_proj.empty:
        indicadores(df_proj)

    colunas = ["ID Winity", "ID Operadora", "Candidato", "Rev.", "Latitude", "Longitude", "Município", "UF", "Rodovia", "KM", "Sentido", "Status"]
    st.dataframe(df_proj[colunas], use_container_width=True)

    sites = df_proj["ID Winity"].unique()
    site_sel = st.selectbox("Selecione um site para detalhes:", sites)
    if st.button("Ver detalhes"):
        st.session_state.site = site_sel
        st.session_state.projetos = projetos_sel
        st.session_state.pagina = "detalhe"
        st.rerun()

def pagina_detalhe():
    df = carregar_dados()
    projetos = st.session_state.get("projetos", [])
    site = st.session_state.get("site", "")
    df_site = df[(df["ID Winity"] == site)]

    st.image("logo_vante.png", width=160)
    st.subheader(f"Projeto(s): {', '.join(projetos)} | Site: {site}")
    if st.button("🔙 VER TODOS OS SITES DO PROJETO"):
        st.session_state.pagina = "tabela"
        st.rerun()

    candidatos = df_site["Candidato"].unique()
    candidato_sel = st.selectbox("Candidato:", candidatos)
    dados = df_site[df_site["Candidato"] == candidato_sel].iloc[0]

    col1, col2 = st.columns([2, 2])
    with col1:
        st.markdown("### Dados do Site")
        campos = {
            "ID OPERADORA": dados.get("ID Operadora", "-"),
            "MUNICÍPIO": dados.get("Município", "-"),
            "UF": dados.get("UF", "-"),
            "RODOVIA": dados.get("Rodovia", "-"),
            "KM": dados.get("KM", "-"),
            "SENTIDO": dados.get("Sentido", "-"),
            "LAT": dados.get("Latitude", "-"),
            "LONG": dados.get("Longitude", "-"),
            "ALTURA": dados.get("Altura da Torre", "-"),
            "RESTRIÇÃO COMAR": dados.get("COMAR", "-"),
            "ENERGIA": dados.get("Energia", "-"),
            "RELEVO": dados.get("Relevo", "-"),
            "ACIONAMENTO": dados.get("Acionamento", "-"),
            "VOO": dados.get("Data Voo", "-"),
            "SAR": dados.get("SAR", "-"),
            "QUALIFICADO": dados.get("Qualificação", "-"),
            "QUALIFICADO OPERADORA": dados.get("Qualificação Operadora", "-"),
            "QUALIFICADO CONCESSIONÁRIA": dados.get("Qualificação Concessionária", "-"),
            "KIT ELABORADO": dados.get("Kit", "-"),
            "KIT APROVADO": dados.get("Aprovação Concessionária", "-"),
            "EM ANÁLISE AGÊNCIA": dados.get("Análise Agência", "-"),
            "PUBLICAÇÃO DO": dados.get("Publicação DO", "-"),
            "EMISSÃO CPEU": dados.get("Emissão CPEU", "-")
        }
        for k, v in campos.items():
            st.markdown(f"**{k}:** {v if v else '-'}")

        st.markdown("### Documentos para Download")
        for nome in ["SAR", "KMZ", "PLANIALTIMETRICO", "PUBLICAÇÃO DIÁRIO", "CPEU"]:
            st.download_button(label=nome, data="Arquivo Simulado", file_name=f"{nome}_{site}.pdf")

    with col2:
        st.markdown("### Localização")
        try:
            lat = float(dados.get("Latitude", -23.0))
            lon = float(dados.get("Longitude", -46.0))
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], popup=f"{site} - Candidato {candidato_sel}").add_to(m)
            st_folium(m, width=700, height=500)
        except:
            st.warning("Coordenadas inválidas para exibição do mapa.")

if st.session_state.pagina == "tabela":
    pagina_tabela()
else:
    pagina_detalhe()
