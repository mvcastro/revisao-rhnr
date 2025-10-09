from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, cast, get_args

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

from revisao_rhnr.databases.database_access import (
    ColunaEstacaoValidadaRHNR,
    ColunaRHNRInicial,
    ColunaRHNRProposta,
    retorna_estacoes_rhnr_proposta,
    retorna_estacoes_rhnr_selecao_inicial,
    retorna_estacoes_validadas_rhnr,
    retorna_objetivos_especificos,
)

load_dotenv()


class PropotaOperacaoEstacao(StrEnum):
    TRNASFERIR = "Transferir"
    MANTER = "Manter"
    DESATIVAR = "Desativar"
    INSTALAR = "Instalar"


COL_RHNR_INICIAL = get_args(ColunaRHNRInicial)
COL_RHNR_PROPOSTA = get_args(ColunaRHNRProposta)

type ColunaTabelaRHNRInicial = Literal[
    "Código da Estação",
    "Nome",
    "Responsável",
    "Operadora",
    "Bacia",
    "Operando",
    "RHNR Implementada",
    "Objetivo 1",
    "Objetivo 2",
    "Objetivo 3",
    "Objetivo 4",
    "Objetivo 5",
    "Objetivo 6",
]


type ColunaTabelaRHNRProposta = Literal[
    "Código da Estação",
    "Nome",
    "Responsável",
    "Operadora",
    "Bacia",
    "Operando",
    "Tipologia Atual",
    "RHNR Inicial?",
    "RHNR Implementada",
    "Ação Proposta",
    "Tipologia Proposta",
    "Integra RHNR?",
    "Objs. Específicos",
]


def formatar_campo_descricao(estacoes: list[dict]) -> list[dict]:
    estacoes_modificadas = []
    for estacao in estacoes:
        nova_estacao = {}
        for key, value in estacao.items():
            if key == "Descrição":
                nova_estacao["RHNR Implementada"] = "RHNR" in str(value)
            else:
                nova_estacao[key] = value
        estacoes_modificadas.append(nova_estacao)
    return estacoes_modificadas


@st.cache_resource
def get_db_engine(url: str):
    return create_engine(url)


@st.cache_data
def get_estacoes_selecao_inicial_rhnr(
    _engine: Engine,
) -> list[dict[ColunaTabelaRHNRInicial, Any]]:
    estacoes = retorna_estacoes_rhnr_selecao_inicial(_engine)
    estacoes_modificadas = formatar_campo_descricao(estacoes)
    return cast(list[dict[ColunaTabelaRHNRInicial, Any]], estacoes_modificadas)


@st.cache_data
def get_estacoes_validadas_rhnr(
    _engine: Engine,
) -> list[dict[ColunaEstacaoValidadaRHNR, Any]]:
    estacoes = retorna_estacoes_validadas_rhnr(_engine)
    estacoes_modificadas = formatar_campo_descricao(estacoes)
    return cast(list[dict[ColunaEstacaoValidadaRHNR, Any]], estacoes_modificadas)


@st.cache_data
def get_estacoes_proposta_rhnr(
    _engine: Engine,
) -> list[dict[ColunaTabelaRHNRProposta, Any]]:
    estacoes = retorna_estacoes_rhnr_proposta(_engine)
    estacoes_modificadas = formatar_campo_descricao(estacoes)
    return cast(list[dict[ColunaTabelaRHNRProposta, Any]], estacoes_modificadas)


@st.cache_data
def get_objetivos_especificos(_engine: Engine) -> list[dict]:
    objs_esps = retorna_objetivos_especificos(_engine)
    result = []
    for objs in objs_esps:
        lista_objs = [
            nome_obj[4:]
            for nome_obj, tem_obj in objs.items()
            if tem_obj and nome_obj != "codigo"
        ]
        result.append(
            {
                "Código da Estação": objs["codigo"],
                "Objs. Específicos": ", ".join(lista_objs),
            }
        )
    return result


@st.cache_data
def join_dataframes_proposta_rhnr(
    df1: pd.DataFrame, df2: pd.DataFrame, filtro: list[dict]
):
    df = df1.merge(df2, on="Código da Estação", how="left")
    df["RHNR Inicial?"] = df["Código da Estação"].isin(
        [est["Código da Estação"] for est in filtro]
    )
    return df


# database_url = os.getenv("DATABASE_URL")
database_url = f"sqlite:///{Path.cwd() / 'revisao_rhnr' / 'databases' / 'database.db'}"
# print(database_url)
# st.stop()

if not database_url:
    st.error("DATABASE_URL not set in environment variables.")
    st.stop()

engine = get_db_engine(database_url)
dict_rhrnr_inicial = get_estacoes_selecao_inicial_rhnr(engine)
df_rhnr_inicial = pd.DataFrame(dict_rhrnr_inicial)

dict_estacoes_validadas = get_estacoes_validadas_rhnr(engine)
df_estacoes_validadas = pd.DataFrame(dict_estacoes_validadas)

estacoes_rhnr_proposta = get_estacoes_proposta_rhnr(engine)
objetivos_especificos = get_objetivos_especificos(engine)
df_rhnr_proposta = join_dataframes_proposta_rhnr(
    pd.DataFrame(estacoes_rhnr_proposta),
    pd.DataFrame(objetivos_especificos),
    dict_rhrnr_inicial,
)[list(get_args(ColunaTabelaRHNRProposta.__value__))]
