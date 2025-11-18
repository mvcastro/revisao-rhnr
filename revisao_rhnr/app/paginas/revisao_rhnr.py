from io import BytesIO
from typing import Sequence, cast, get_args

import numpy as np
import pandas as pd
import streamlit as st

from revisao_rhnr.app.data import (
    ColunaTabelaRHNRProposta,
    df_estacoes_validadas,
    df_rhnr_inicial,
    df_rhnr_proposta,
)
from revisao_rhnr.app.paginas.dataframe_styling import highlight_rows_by_category

select_options: tuple[ColunaTabelaRHNRProposta] = get_args(
    ColunaTabelaRHNRProposta.__value__
)


def padroniza_dicionario_rhnr(dataframe: pd.DataFrame) -> dict:
    dicionario = {}
    total_linhas = dataframe.shape[0]
    for col in dataframe.columns:
        if "Objetivo" in col:
            continue
        if col in select_options:
            dicionario[col] = dataframe[col].to_list()
        else:
            dicionario[col] = [None] * total_linhas
    return dicionario


@st.cache_data
def adiciona_estacoes_rhrn_inicial_e_validadas() -> pd.DataFrame:
    dict_rede_inicial = padroniza_dicionario_rhnr(df_rhnr_inicial)
    df_rede_inicial = pd.DataFrame(dict_rede_inicial)
    df_rede_inicial["RHNR Inicial?"] = True
    df_rede_inicial_sem_proposta = df_rede_inicial[
        ~df_rede_inicial["Código da Estação"].isin(
            df_rhnr_proposta["Código da Estação"]
        )
    ]

    dict_estacoes_validadas = padroniza_dicionario_rhnr(df_estacoes_validadas)
    df_rede_validada = pd.DataFrame(dict_estacoes_validadas)
    df_rede_validada_sem_inicial = df_rede_validada[
        ~df_rede_validada["Código da Estação"].isin(
            df_rede_inicial["Código da Estação"]
        )
    ].copy()
    df_rede_validada_sem_inicial["RHNR Inicial?"] = False
    df_rede_validada_sem_inicial_e_sem_proposta = df_rede_validada_sem_inicial[
        ~df_rede_validada_sem_inicial["Código da Estação"].isin(
            df_rhnr_proposta["Código da Estação"]
        )
    ]

    df_concat = (
        pd.concat(
            [
                df_rhnr_proposta,
                df_rede_inicial_sem_proposta,
                df_rede_validada_sem_inicial_e_sem_proposta,
            ]
        )
        .sort_values(by="Código da Estação")
        .reset_index(drop=True)
    )

    # df_concat["Integra RHNR?"] = df_concat["Integra RHNR?"].fillna(False)

    return df_concat


@st.cache_data
def create_dictionary_select_options(
    dataframe: pd.DataFrame, columns: Sequence[ColunaTabelaRHNRProposta]
) -> dict[ColunaTabelaRHNRProposta, list[str]]:
    result = {}
    for column in columns:
        result[column] = (
            dataframe[column].replace(np.nan, None).sort_values().unique().tolist()
        )
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
        "#a6cee3",
        "#1f78b4",
        "#b2df8a",
        "#33a02c",
        "#fb9a99",
        "#e31a1c",
        "#fdbf6f",
        "#ff7f00",
        "#cab2d6",
        "#6a3d9a",
        "#ffff99",
        "#b15928",
    ]

    df_rhnr_final = adiciona_estacoes_rhrn_inicial_e_validadas()

    select_dicionario = create_dictionary_select_options(df_rhnr_final, select_options)

    pills_options: list[ColunaTabelaRHNRProposta] = [
        "Responsável",
        "Operadora",
        "Bacia",
        "Operando",
        "RHNR Implementada?",
        "RHNR Inicial?",
        "Integra RHNR?",
        "Ação Proposta",
    ]

    coluna1, coluna2 = st.columns(2, vertical_alignment="center", border=True)

    with coluna1:
        select_campo1 = st.selectbox(
            label="Campo da tabela:",
            index=None,
            options=list(select_dicionario.keys()),
            placeholder="Selecione um campo da tabela para filtrar",
            key="select_campo1",
        )

    with coluna2:
        if not select_campo1:
            valores_filtro1 = st.selectbox(
                label="Valor do Filtro:",
                options=[""],
                disabled=True,
                key="valores_filtro1",
            )
        else:
            valores_filtro1 = st.selectbox(
                label="Selecione o valor a filtar:",
                index=None,
                options=[
                    option
                    for option in select_dicionario[select_campo1]
                    if option is not None
                ],  # type: ignore
                placeholder=f"Selecione um valor do campo {select_campo1} para filtrar",
                key="valores_filtro1",
            )

    coluna3, coluna4 = st.columns(2, vertical_alignment="center", border=True)

    with coluna3:
        select_campo2 = st.selectbox(
            label="Campo da tabela:",
            index=None,
            options=[i for i in list(select_dicionario.keys()) if i != select_campo1],
            placeholder="Selecione um campo da tabela para filtrar",
            key="select_campo2",
        )
    with coluna4:
        if not select_campo2:
            valores_filtro2 = st.selectbox(
                label="Valor do Filtro:",
                options=[""],
                disabled=True,
                key="valores_filtro2",
            )
        else:
            valores_filtro2 = st.selectbox(
                label="Selecione o valor a filtar:",
                index=None,
                options=[
                    option
                    for option in select_dicionario[
                        cast(ColunaTabelaRHNRProposta, select_campo2)
                    ]
                    if option is not None
                ],  # type: ignore
                placeholder=f"Selecione um valor do campo {select_campo2} para filtrar",
                key="valores_filtro2",
            )

    pill_selection = st.pills(
        "Coluna a destacar:", pills_options, selection_mode="single"
    )

    if select_campo1 is not None:
        if valores_filtro1 is None:
            df_selecao = df_rhnr_final[df_rhnr_final[select_campo1].isna()]
        else:
            df_selecao = df_rhnr_final[df_rhnr_final[select_campo1] == valores_filtro1]
    else:
        df_selecao = df_rhnr_final

    if select_campo2 is not None:
        if valores_filtro2 is None:
            df_selecao = df_selecao[df_selecao[select_campo2].isna()]
        else:
            df_selecao = df_selecao[df_selecao[select_campo2] == valores_filtro2]

    coluna3, coluna4 = st.columns([0.6, 0.4], vertical_alignment="center")

    with coluna3:
        st.subheader("Tabela de Revisão da RHNR")
    with coluna4:
        st.subheader(f"Número de estações selecionadas: {df_selecao.shape[0]}")

    if pill_selection:
        pill_dictionary = create_dictionary_select_options(df_selecao, pills_options)
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

    st.download_button(
        label="Download da Tabela",
        data=to_excel(df_selecao),
        mime="application/vnd.ms-excel",
        file_name="revisao_rhnr.xlsx",
        type="primary",
    )


def to_excel(df):
    """
    Converts a Pandas DataFrame to an Excel file in-memory.
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="openpyxl")
    df.to_excel(writer, index=False)
    writer.close()  # Use writer.close() instead of writer.save() for newer pandas versions
    processed_data = output.getvalue()
    return processed_data
