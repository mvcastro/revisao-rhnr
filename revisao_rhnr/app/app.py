import streamlit as st

from revisao_rhnr.app.paginas.relatorio_selecao_inicial import (
    relatorio_selecao_inicial,
)
from revisao_rhnr.app.paginas.relatorio_selecao_proposta import (
    relatorio_selecao_proposta,
)
from revisao_rhnr.app.paginas.revisao_rhnr import revisao_rhnr

st.set_page_config(page_title="Revisão RHNR", layout="wide")
tab1, tab2, tab3 = st.tabs(
    [
        "Relatório - Seleção Inicial RHNR",
        "Relatório - Seleção RHNR Proposta",
        "Análise e Revisão RHNR",
    ]
)

with tab1:
    relatorio_selecao_inicial()
with tab2:
    relatorio_selecao_proposta()
with tab3:
    revisao_rhnr()
