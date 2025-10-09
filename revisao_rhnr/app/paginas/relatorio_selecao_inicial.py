import streamlit as st

from revisao_rhnr.app.data import (
    df_rhnr_inicial,
)

@st.cache_data
def relatorio_selecao_inicial():
    st.header("Relatório de Estações - Seleção Inicial RHNR")

    st.subheader("Estações da seleção inicial da RHNR corrigidas:")
    st.markdown(
        "Estações não existentes no Hidro: ***[10100001, 11500001, 12351001]***"
    )
    st.markdown(
        "Código das estações corrigidas para ***10100000, 11500000, 12351000***, respectivamente."
    )

    st.dataframe(
        df_rhnr_inicial[df_rhnr_inicial["Código"].isin([10100000, 11500000, 12351000])],
        hide_index=True,
    )

    df_rhnr_inicial_nao_operando = df_rhnr_inicial[df_rhnr_inicial["Operando"] == 0]
    st.subheader(
        f"Estações da seleção inicial da RHNR não operando ({df_rhnr_inicial_nao_operando.shape[0]}):"
    )
    st.dataframe(df_rhnr_inicial_nao_operando, hide_index=True)

    df_rhnr_inicial_operando = df_rhnr_inicial[df_rhnr_inicial["Operando"] == 1]
    st.subheader(
        f"Estações da seleção inicial da RHNR operando ({df_rhnr_inicial_operando.shape[0]}):"
    )
    st.dataframe(df_rhnr_inicial_operando, hide_index=True)
