import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Carregar dados reais da planilha
@st.cache_data

def carregar_dados():
    file_path = "EcoRiominas - Status Sites.xlsx"
    df = pd.read_excel(file_path, sheet_name="Controle")
    df = df.dropna(subset=["ID Winity", "Candidato"])
    df = df[df["Candidato"].isin(["A", "B", "C", "D"])]
    df = df.fillna("")
    return df

# Inicializar app
st.set_page_config(layout="wide")
st.title("Painel Vante - Controle de Sites")

df = carregar_dados()
site_ids = df["ID Winity"].unique()
site_selecionado = st.selectbox("Selecione um site:", site_ids)

site_data = df[df["ID Winity"] == site_selecionado]

col1, col2 = st.columns([2, 2])

with col1:
    st.subheader(f"Detalhamento - {site_selecionado}")
    candidatos = site_data["Candidato"].unique()
    for cand in sorted(candidatos):
        candidato_data = site_data[site_data["Candidato"] == cand].iloc[0]
        st.markdown(f"### Candidato [{cand}] - Revisão 0")  # Regra: novo candidato inicia em 0
        st.markdown(f"**Operadora:** {candidato_data['ID Operadora']}")
        st.markdown(f"**Status:** {candidato_data['STATUS']}")
        st.markdown(f"**Observações:** {candidato_data['Obs'] if candidato_data['Obs'] else '-'}")

        arquivos = ["SAR.pdf", "Projeto_Estrutura.pdf"] if candidato_data['STATUS'] else []
        if arquivos:
            st.markdown("**Arquivos disponíveis:**")
            for file in arquivos:
                st.download_button(label=file, data="Arquivo Simulado", file_name=file)
        st.markdown("---")

with col2:
    st.subheader("Localização dos Candidatos")
    primeiro = site_data.iloc[0]
    lat = primeiro.get("Latitude Candidato", -23.0)
    lon = primeiro.get("Longitude Candidato", -46.0)
    m = folium.Map(location=[lat, lon], zoom_start=14)
    for _, row in site_data.iterrows():
        if row["Latitude Candidato"] and row["Longitude Candidato"]:
            folium.Marker([row["Latitude Candidato"], row["Longitude Candidato"]],
                          popup=f"Candidato {row['Candidato']}\nStatus: {row['STATUS']}").add_to(m)
    st_folium(m, width=700, height=500)

st.markdown("---")
st.caption("Protótipo inicial com base real - Painel Vante | Desenvolvido com Streamlit")
