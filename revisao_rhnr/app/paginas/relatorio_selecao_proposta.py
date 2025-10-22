import streamlit as st

from revisao_rhnr.app.data import (
    df_estacoes_rhnr_proposta,
    df_rhnr_inicial,
    df_rhnr_proposta,
)
from revisao_rhnr.app.paginas.dataframe_styling import highlight_rows_by_category


@st.cache_data
def relatorio_selecao_proposta():
    df_rhnr_filtro = df_rhnr_inicial[
        df_rhnr_inicial["Código da Estação"].isin(
            df_estacoes_rhnr_proposta[
                (~df_estacoes_rhnr_proposta["Integra RHNR?"].isnull()) &
                (df_estacoes_rhnr_proposta["Integra RHNR?"])][
                "Código da Estação"
            ]
        )
    ]

    df_rhnr_perm = df_rhnr_proposta[
        df_rhnr_proposta["Código da Estação"].isin(df_rhnr_filtro["Código da Estação"])
    ]

    st.subheader(
        f"Estações da Seleção Inicial RHNR que permaneceram na lista de Revisão da RHNR({df_rhnr_perm.shape[0]}):"
    )
    st.text("✅ Estações em operação 🔴 Estações não operando")
    st.dataframe(
        df_rhnr_perm.style.apply(
            highlight_rows_by_category,
            axis=1,
            column="Operando",
            match_values=[0, 1],
            colors=["#ffe6e6", "#e6fff2"],
        ),
        hide_index=True,
    )

    df_rhnr_adicionais = df_rhnr_proposta[
        ~df_rhnr_proposta["Código da Estação"].isin(
            df_rhnr_inicial["Código da Estação"]
        )
    ]

    st.subheader(
        f"Estações que passaram a fazer parte da RHNR com a Revisão ({df_rhnr_adicionais.shape[0]}):"
    )
    st.text("✅ Estações em operação 🔴 Estações não operando")
    st.dataframe(
        df_rhnr_adicionais.style.apply(
            highlight_rows_by_category,
            axis=1,
            column="Operando",
            match_values=[0, 1],
            colors=["#ffe6e6", "#e6fff2"],
        ),
        hide_index=True,
    )
