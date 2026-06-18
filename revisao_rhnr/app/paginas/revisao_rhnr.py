from io import BytesIO
from typing import Literal, Sequence, cast, get_args

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

type TipoOpcoes = float | str | bool | None

CONVERSOR_OPCOES: dict[bool | None, str] = {True: "Sim", False: "Não", None: "Nulo"}
CONVERSOR_OPCOES2: dict[Literal["Sim", "Não", "Nulo"], bool | None] = {
    "Sim": True,
    "Não": False,
    "Nulo": None,
}


select_options: tuple[ColunaTabelaRHNRProposta] = get_args(
    ColunaTabelaRHNRProposta.__value__
)


def converte_bool_to_str(valor: TipoOpcoes) -> str | float:
    conversor: dict[bool | None, str] = {True: "Sim", False: "Não", None: "Nulo"}
    if valor is None or isinstance(valor, bool):
        return conversor[valor]
    return valor


def converte_str_to_bool(valor: TipoOpcoes) -> TipoOpcoes:
    conversor: dict[Literal["Sim", "Não", "Nulo"], bool | None] = {
        "Sim": True,
        "Não": False,
        "Nulo": None,
    }

    if valor in ["Sim", "Não", "Nulo"]:
        return conversor[cast(Literal["Sim", "Não", "Nulo"], valor)]
    return valor


def padroniza_dicionario_rhnr(
    dataframe: pd.DataFrame,
) -> dict[TipoOpcoes, list[TipoOpcoes]]:
    dicionario: dict[TipoOpcoes, list[TipoOpcoes]] = {}
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
) -> dict[ColunaTabelaRHNRProposta, list[TipoOpcoes]]:
    result: dict[ColunaTabelaRHNRProposta, list[TipoOpcoes]] = {}
    for column in columns:
        result[column] = (
            dataframe[column].replace(np.nan, None).sort_values().unique().tolist()
        )
    return result


def filtro_dataframe(
    df: pd.DataFrame, select_campo: str | None = None, valores_filtro: TipoOpcoes = None
) -> pd.DataFrame:
    if select_campo is not None:
        if valores_filtro is None:
            return df[df[select_campo].isna()]
        else:
            return df[df[select_campo] == valores_filtro]
    else:
        return df


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

    col_check1, col_check2 = st.columns([0.2, 0.8], vertical_alignment="center")
    with col_check1:
        responsavel_ana = st.checkbox(label="Somente Responsável ANA", value=True)
    with col_check2:
        em_operacao = st.checkbox(label="Somente Estações em Operação", value=True)

    df_selecao = (
        df_rhnr_final[df_rhnr_final["Responsável"] == "ANA"]
        if responsavel_ana
        else df_rhnr_final
    )

    df_selecao = df_selecao[df_selecao["Operando"] == 1] if em_operacao else df_selecao

    colunas1 = st.columns(2, vertical_alignment="center", border=True)

    with colunas1[0]:
        select_campo1 = st.selectbox(
            label="Campo da tabela:",
            index=None,
            options=list(select_dicionario.keys()),
            placeholder="Selecione um campo da tabela para filtrar",
            key="select_campo1",
        )

    with colunas1[1]:
        if not select_campo1:
            valor_filtro1 = st.selectbox(
                label="Valor do Filtro:",
                options=[""],
                disabled=True,
                key="valores_filtro1",
            )
        else:
            valor_filtro1 = st.selectbox(
                label="Selecione o valor a filtar:",
                index=None,
                options=[
                    converte_bool_to_str(option)
                    for option in select_dicionario[select_campo1]
                ],
                placeholder=f'Selecione um valor do campo " {select_campo1} " para filtrar',
                key="valores_filtro1",
            )
    filtro1 = None
    if valor_filtro1:
        filtro1 = converte_str_to_bool(valor_filtro1)
        df_selecao_out = filtro_dataframe(df_selecao, select_campo1, filtro1)
    else:
        df_selecao_out = df_selecao
    condicao1 = st.radio(label="condição 1", options=["E", "OU"], horizontal=True)
    colunas2 = st.columns(2, vertical_alignment="center", border=True)

    with colunas2[0]:
        disable_campo2 = True
        if valor_filtro1:
            disable_campo2 = False

        select_campo2 = st.selectbox(
            label="Campo da tabela:",
            index=None,
            options=[i for i in list(select_dicionario.keys()) if i != select_campo1],
            placeholder="Selecione um campo da tabela para filtrar",
            key="select_campo2",
            disabled=disable_campo2,
        )
    with colunas2[1]:
        if not select_campo2:
            valor_filtro2 = st.selectbox(
                label="Valor do Filtro:",
                options=[""],
                disabled=True,
                key="valores_filtro2",
            )
        else:
            valor_filtro2 = st.selectbox(
                label="Selecione o valor a filtar:",
                index=None,
                options=[
                    converte_bool_to_str(option)
                    for option in select_dicionario[
                        cast(ColunaTabelaRHNRProposta, select_campo2)
                    ]
                ],
                placeholder=f"Selecione um valor do campo {select_campo2} para filtrar",
                key="valores_filtro2",
            )

    filtro2 = None
    if valor_filtro2:
        filtro2 = converte_str_to_bool(valor_filtro2)

    if condicao1 == "E" and all([filtro1, filtro2]):
        df_selecao_out = filtro_dataframe(df_selecao_out, select_campo2, filtro2)
    if condicao1 == "OU" and all([filtro1, filtro2]):
        df_selecao_filtro1 = filtro_dataframe(df_selecao, select_campo1, filtro1)
        df_selecao_filtro2 = filtro_dataframe(df_selecao, select_campo2, filtro2)
        df_selecao_out = pd.concat(
            [df_selecao_filtro1, df_selecao_filtro2]
        ).drop_duplicates()

    condicao2 = st.radio(label="condição 2", options=["E", "OU"], horizontal=True)
    colunas3 = st.columns(2, vertical_alignment="center", border=True)

    with colunas3[0]:
        select_campo3 = st.selectbox(
            label="Campo da tabela:",
            index=None,
            options=[i for i in list(select_dicionario.keys()) if i != select_campo2],
            placeholder="Selecione um campo da tabela para filtrar",
            key="select_campo3",
        )
    with colunas3[1]:
        if not select_campo3:
            valor_filtro3 = st.selectbox(
                label="Valor do Filtro:",
                options=[""],
                disabled=True,
                key="valores_filtro3",
            )
        else:
            valor_filtro3 = st.selectbox(
                label="Selecione o valor a filtar:",
                index=None,
                options=[
                    converte_bool_to_str(option)
                    for option in select_dicionario[
                        cast(ColunaTabelaRHNRProposta, select_campo3)
                    ]
                ],
                placeholder=f"Selecione um valor do campo {select_campo3} para filtrar",
                key="valores_filtro3",
            )

    filtro3 = None
    if valor_filtro3:
        filtro3 = converte_str_to_bool(valor_filtro3)

    if condicao2 == "E" and all([filtro1, filtro2, filtro3]):
        df_selecao_out = filtro_dataframe(df_selecao_out, select_campo2, filtro3)
    if condicao2 == "OU" and all([filtro1, filtro2, filtro3]):
        df_selecao_filtro3 = filtro_dataframe(df_selecao, select_campo3, filtro3)
        df_selecao_out = pd.concat(
            [df_selecao_out, df_selecao_filtro3]
        ).drop_duplicates()

    pill_selection = st.pills(
        "Coluna a destacar:", pills_options, selection_mode="single"
    )

    colunas3 = st.columns([0.6, 0.4], vertical_alignment="center")

    with colunas3[0]:
        st.subheader("Tabela de Revisão da RHNR")
    with colunas3[1]:
        st.subheader(f"Número de estações selecionadas: {df_selecao_out.shape[0]}")

    if pill_selection:
        pill_dictionary = create_dictionary_select_options(
            df_selecao_out, pills_options
        )
        st.dataframe(
            df_selecao_out.style.apply(
                highlight_rows_by_category,
                axis=1,
                column=pill_selection,  # type: ignore
                match_values=pill_dictionary[pill_selection],  # type: ignore
                colors=colors[0 : len(pill_dictionary[pill_selection])],  # type: ignore
            ),
            hide_index=True,
        )
    else:
        st.dataframe(df_selecao_out, hide_index=True)

    st.download_button(
        label="Download da Tabela",
        data=to_excel(df_selecao_out),
        mime="application/vnd.ms-excel",
        file_name="revisao_rhnr.xlsx",
        type="primary",
    )


def to_excel(df: pd.DataFrame):
    """
    Converts a Pandas DataFrame to an Excel file in-memory.
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="openpyxl")
    df.to_excel(writer, index=False)  # type: ignore
    writer.close()  # Use writer.close() instead of writer.save() for newer pandas versions
    processed_data = output.getvalue()
    return processed_data
