
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------- Configuração Inicial ----------
st.set_page_config(layout="wide")

if "pagina" not in st.session_state:
    st.session_state.pagina = "tabela"
    st.session_state.site = ""
    st.session_state.projeto = []
    st.session_state.filtro_status = None

@st.cache_data
def carregar_dados():
    df = pd.read_excel("Status Sites.xlsx", sheet_name="Planilha1")
    df = df.dropna(subset=["ID Winity", "Candidato"])
    df = df[df["Candidato"].isin(["A", "B", "C", "D"])]
    df = df.fillna("")
    return df

# ---------- Página 1: Painel de Projetos ----------
def pagina_tabela():
    st.image("logo_vante.png", width=160)
    df = carregar_dados()

    projetos = st.multiselect("Selecione o Projeto:", df["Projeto"].unique(), default=st.session_state.projeto)
    st.session_state.projeto = projetos

    if not projetos:
        return

    df_filtrado = df[df["Projeto"].isin(projetos)]

    # ---------- Selecionar apenas um candidato vigente por site ----------
    df_filtrado = df_filtrado.sort_values(by=["ID Winity", "Rev."], ascending=[True, False])
    df_filtrado = df_filtrado.groupby("ID Winity").apply(
        lambda x: x[x["STATUS"].str.lower().isin(["em qualificação", "qualificado"])] if any(
            x["STATUS"].str.lower().isin(["em qualificação", "qualificado"])) else x).reset_index(drop=True)
    df_filtrado = df_filtrado.sort_values(by=["ID Winity", "Rev."], ascending=[True, False])
    df_filtrado = df_filtrado.drop_duplicates(subset=["ID Winity"], keep="first")

    etapas = {
        "TOTAL DE SITES": "# 📍",
        "VOADO": "🛩️",
        "PROCESSAMENTO VOO": "📰",
        "SAR": "📄",
        "QUALIFICADO": "✅",
        "QUALIFICADO OPERADORA": "📊",
        "QUALIFICADO CONCESSIONÁRIA": "🏛️",
        "KIT ELABORADO": "🥇",
        "KIT APROVADO": "✔️",
        "EM ANÁLISE AGÊNCIA": "🔍",
        "PUBLICAÇÃO DO": "📰",
        "EMISSÃO CPEU": "📄"
    }

    def indicadores(df):
        total = len(df)
        cards = []
        for etapa, icone in etapas.items():
            if etapa == "TOTAL DE SITES":
                cards.append((etapa, icone, total))
            elif etapa == "VOADO":
                cards.append((etapa, icone, df["VOO"].astype(str).str.strip().ne("").sum()))
            elif etapa == "PROCESSAMENTO VOO":
                cards.append((etapa, icone, df["Processamento Voo"].astype(str).str.strip().ne("").sum()))
            elif etapa == "EMISSÃO CPEU":
                cards.append((etapa, icone, df["Emissão CPEU"].astype(str).str.strip().ne("").sum()))
            else:
                cards.append((etapa, icone, df["STATUS"].str.upper().str.contains(etapa.upper()).sum()))
        return cards

    colunas = st.columns(len(etapas))
    for i, (etapa, icone, valor) in enumerate(indicadores(df_filtrado)):
        if etapa == "TOTAL DE SITES":
            colunas[i].metric(f"{icone} {etapa}", valor)
        else:
            if colunas[i].button(f"{icone} {etapa}
{valor}"):
                st.session_state.filtro_status = etapa

    if st.session_state.filtro_status:
        df_filtrado = df_filtrado[df_filtrado["STATUS"].str.upper().str.contains(st.session_state.filtro_status.upper())]

    def gerar_link(site_id):
        return f"[{site_id}](#{site_id})"

    df_filtrado["ID Winity"] = df_filtrado["ID Winity"].apply(gerar_link)

    tabela = df_filtrado[["ID Winity", "ID Operadora", "Candidato", "Rev.", "Município", "UF", "Rodovia", "KM", "Sentido", "STATUS"]]
    st.markdown(tabela.to_markdown(index=False), unsafe_allow_html=True)

    site_escolhido = st.selectbox("Selecione um site para detalhes:", df_filtrado["ID Winity"].str.extract(r'\[(.*?)\]')[0])
    if st.button("Ver detalhes"):
        st.session_state.site = site_escolhido
        st.session_state.pagina = "detalhe"
        st.rerun()

# ---------- Página 2: Detalhamento do Site ----------
def pagina_detalhe():
    df = carregar_dados()
    site = st.session_state.site
    dados = df[df["ID Winity"] == site].iloc[0]

    st.image("logo_vante.png", width=160)
    st.subheader(f"Detalhamento - {site}")

    if st.button("🔙 VER TODOS OS SITES DO PROJETO"):
        st.session_state.pagina = "tabela"
        st.rerun()

    st.markdown(f"**Candidato:** {dados['Candidato']}")
    st.markdown(f"**Operadora:** {dados['ID Operadora']}")
    st.markdown(f"**Status:** {dados['STATUS']}")
    st.markdown(f"**Observações:** {dados.get('Observação', '-')}")

    st.markdown("**Arquivos disponíveis:**")
    for arq in ["SAR.pdf", "Projeto_Estrutura.pdf"]:
        st.download_button(arq, data=b"Fake content", file_name=arq)

# ---------- Execução ----------
if st.session_state.pagina == "tabela":
    pagina_tabela()
else:
    pagina_detalhe()
