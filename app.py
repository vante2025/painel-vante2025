import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------- Configuração Inicial ----------
st.set_page_config(layout="wide")

if "pagina" not in st.session_state:
    st.session_state.pagina = "tabela"

@st.cache_data
def carregar_dados():
    file_path = "EcoRiominas - Status Sites.xlsx"
    df = pd.read_excel(file_path, sheet_name="Controle")
    df = df.dropna(subset=["ID Winity", "Candidato"])
    df = df[df["Candidato"].isin(["A", "B", "C", "D"])]
    df = df.fillna("")
    return df

# ---------- Função para exibir logo do projeto ----------
def exibir_logo_projeto(nome_projeto):
    caminho_logo = f"logo_{nome_projeto.lower().replace(' ', '_')}.png"
    try:
        st.image(caminho_logo, width=120)
    except:
        st.warning(f"Logo não encontrado para o projeto: {nome_projeto}")

# ---------- Página 1: Tabela por Projeto ----------
def pagina_tabela():
    st.image("logo_vante.png", width=160)
    st.title("Selecione um projeto")

    df = carregar_dados()

    if "Projeto" not in df.columns:
        st.error("A coluna 'Projeto' não está presente na planilha.")
        return

    projeto = st.selectbox("PROJETO:", df["Projeto"].unique())
    exibir_logo_projeto(projeto)

    # Filtrar apenas candidatos vigentes
    candidatos_validos = df[
        (df["Projeto"] == projeto) &
        (~df["STATUS"].str.lower().str.contains("obsoleto|reprovado|invalidado"))
    ]

    colunas = ["ID Winity", "ID Operadora", "Candidato", "STATUS", "Latitude Candidato", "Longitude Candidato",
               "Município", "UF", "Rodovia", "KM", "Sentido"]

    tabela = candidatos_validos[colunas]
    st.dataframe(tabela, use_container_width=True, hide_index=True)

    site_escolhido = st.selectbox("Selecione um site para detalhes:", tabela["ID Winity"].unique())
    if st.button("Ver detalhes do site"):
        st.session_state.site = site_escolhido
        st.session_state.projeto = projeto
        st.session_state.pagina = "detalhe"
        st.rerun()

# ---------- Página 2: Detalhamento ----------
def pagina_detalhe():
    df = carregar_dados()
    projeto = st.session_state.get("projeto", "")
    site = st.session_state.get("site", "")
    df_site = df[(df["Projeto"] == projeto) & (df["ID Winity"] == site)]

    st.image("logo_vante.png", width=160)
    exibir_logo_projeto(projeto)

    st.subheader(f"Projeto: {projeto} | Site: {site}")
    if st.button("🔙 VER TODOS OS SITES DO PROJETO"):
        st.session_state.pagina = "tabela"
        st.rerun()

    candidatos = df_site["Candidato"].unique()
    candidato_sel = st.selectbox("Candidato:", candidatos)
    rev = "0"

    dados = df_site[df_site["Candidato"] == candidato_sel].iloc[0]

    col1, col2 = st.columns([2, 2])

    with col1:
        st.markdown("### Dados do Site")
        campos = {
            "ID OPERADORA": dados["ID Operadora"],
            "MUNICÍPIO": dados["Município"],
            "UF": dados["UF"],
            "RODOVIA": dados["Rodovia"],
            "KM": dados["KM"],
            "SENTIDO": dados["Sentido"],
            "LAT": dados["Latitude Candidato"],
            "LONG": dados["Longitude Candidato"],
            "DISTÂNCIA PN": dados["Dist PN"],
            "LAT PN": dados["Latitude PN"],
            "LONG PN": dados["Longitude PN"],
            "ALTURA": dados["Altura da Torre Final (m)"],
            "RESTRIÇÃO COMAR": dados["COMAR"],
            "ENERGIA": dados["Energia"],
            "RELEVO": dados["Relevo"],
            "ACIONAMENTO": dados["Acionamento Fornecedor"],
            "VOO": dados["Data Voo"],
            "SAR": dados["SAR"],
            "QUALIFICADO": dados["Validação Aquisição"],
            "QUALIFICADO OPERADORA": dados["SAR QUALIFICADO OPERADORA"],
            "QUALIFICADO CONCESSIONÁRIA": dados["Analise Concessionária"]
        }
        for k, v in campos.items():
            st.markdown(f"**{k}:** {v if v else '-'}")

        st.markdown("### Documentos para Download")
        for nome in ["SAR", "KMZ", "PLANIALTIMETRICO", "PUBLICAÇÃO DIÁRIO", "CPEU"]:
            st.download_button(label=nome, data="Arquivo Simulado", file_name=f"{nome}_{site}.pdf")

    with col2:
        st.markdown("### Localização")
        m = folium.Map(location=[dados["Latitude Candidato"], dados["Longitude Candidato"]], zoom_start=15)
        folium.Marker(
            [dados["Latitude Candidato"], dados["Longitude Candidato"]],
            popup=f"Candidato {candidato_sel}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
        folium.Marker(
            [dados["Latitude PN"], dados["Longitude PN"]],
            popup="Ponto Nominal (PN)",
            icon=folium.Icon(color='green', icon='flag')
        ).add_to(m)
        st_folium(m, width=700, height=500)

if st.session_state.pagina == "tabela":
    pagina_tabela()
else:
    pagina_detalhe()
