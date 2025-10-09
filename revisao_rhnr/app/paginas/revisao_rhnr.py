from typing import Sequence, get_args
import pandas as pd
import streamlit as st

from revisao_rhnr.app.data import (
    df_rhnr_proposta,
)
from revisao_rhnr.app.paginas.dataframe_styling import highlight_rows_by_category
from revisao_rhnr.databases.database_access import ColunaRHNRProposta


@st.cache_data
def create_dictionary_select_options(
    dataframe: pd.DataFrame, columns: Sequence[ColunaRHNRProposta]
) -> dict[ColunaRHNRProposta, list[str]]:
    result = {}
    for column in columns:
        result[column] = dataframe[column].sort_values().unique().tolist()
    return result


def revisao_rhnr() -> None:
    colors = [
        "#8dd3c7",
        "#ffffb3",
        "#bebada",
        "#fb8072",
        "#80b1d3",
        "#fdb462",
        "#b3de69",
        "#fccde5",
        "#d9d9d9",
        "#bc80bd",
        "#ccebc5",
        "#ffed6f",
    ]

    select_options: tuple[ColunaRHNRProposta] = get_args(ColunaRHNRProposta.__value__)

    select_dicionario = create_dictionary_select_options(
        df_rhnr_proposta, select_options
    )

    pills_options: list[ColunaRHNRProposta] = [
        "Responsável",
        "Operadora",
        "Bacia",
        "Operando",
        "Integra RHNR?",
        "Ação Proposta",
        "RHNR Inicial?"
    ]
    pill_dictionary = create_dictionary_select_options(df_rhnr_proposta, pills_options)

    coluna1, coluna2 = st.columns(2, vertical_alignment="center", border=True)

    with coluna1:
        select_campo = st.selectbox(
            label="Campo da tabela:",
            index=None,
            options=list(select_dicionario.keys()),
            placeholder="Selecione um campo da tabela para filtrar",
        )
    with coluna2:
        if not select_campo:
            valores_filtro = st.selectbox(
                label="Valor do Filtro:",
                options=[""],
                disabled=True,
            )
        else:
            valores_filtro = st.selectbox(
                label="Selecione o valor a filtar:",
                index=None,
                options=select_dicionario[select_campo],  # type: ignore
                placeholder=f"Selecione um valor do campo {select_campo} para filtrar",
            )

    pill_selection = st.pills(
        "Coluna a destacar:", pills_options, selection_mode="single"
    )

    if select_campo and valores_filtro:
        df_selecao = df_rhnr_proposta[df_rhnr_proposta[select_campo] == valores_filtro]
    else:
        df_selecao = df_rhnr_proposta

    coluna3, coluna4 = st.columns([0.6, 0.4], vertical_alignment="center")

    with coluna3:
        st.subheader("Tabela de Revisão da RHNR")
    with coluna4:
        st.subheader(f"Número de estações selecionadas: {df_selecao.shape[0]}")

    if pill_selection:
        st.dataframe(
            df_selecao.style.apply(
                highlight_rows_by_category,
                axis=1,
                column=pill_selection,  # type: ignore
                match_values=pill_dictionary[pill_selection],  # type: ignore
                colors=colors[0 : len(pill_dictionary[pill_selection])],  # type: ignore
            ),
            hide_index=True,
        )
    else:
        st.dataframe(df_selecao, hide_index=True)
