from enum import StrEnum
from pathlib import Path
from typing import Literal, get_args

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

from revisao_rhnr.databases.database_access import (
    ColunaRHNRInicial,
    ColunaRHNRProposta,
    retorna_estacoes_flu_por_codigos,
    retorna_estacoes_rhnr_proposta,
    retorna_estacoes_rhnr_selecao_inicial,
    retorna_estacoes_validadas_rhnr,
    retorna_objetivos_especificos,
    retorna_tipologia_da_estacao,
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
    "Tipologia Mapeada",
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
def get_estacoes_potenciais_rhnr(
    _engine: Engine, df_tipo_estacoes: pd.DataFrame
) -> pd.DataFrame:
    cod_ests_potenciais = [
        12370000,
        12530000,
        13169900,
        13405000,
        13572000,
        13700000,
        14526000,
        14526500,
        15558000,
        15558200,
        16368000,
        17091000,
        17093000,
        17120000,
        17210000,
        17343000,
        18422000,
        21300000,
        24070000,
        24200000,
        24780000,
        24900000,
        50250000,
        53790000,
        54549000,
        57476500,
        57490000,
        57550000,
        57650000,
        57700000,
        57720000,
        60010000,
        60790000,
        60930000,
        60968000,
        63900001,
        63930000,
        64506000,
        65095000,
        65948000,
        65950200,
        65990550,
        66260006,
        81160000,
        83069900,
        84071000,
        84300000,
        84551000,
    ]
    estacoes = retorna_estacoes_flu_por_codigos(_engine, cod_ests_potenciais)
    estacoes_modificadas = formatar_campo_descricao(estacoes)
    return pd.DataFrame(estacoes_modificadas).merge(
        df_tipo_estacoes, on="Código da Estação", how="left"
    )


@st.cache_data
def get_estacoes_selecao_inicial_rhnr(
    _engine: Engine, df_tipo_estacoes: pd.DataFrame
) -> pd.DataFrame:
    estacoes = retorna_estacoes_rhnr_selecao_inicial(_engine)
    estacoes_modificadas = formatar_campo_descricao(estacoes)
    return pd.DataFrame(estacoes_modificadas).merge(
        df_tipo_estacoes, on="Código da Estação", how="left"
    )


@st.cache_data
def get_tipologia_estacoes(_engine: Engine) -> pd.DataFrame:
    tipologia_estacoes = retorna_tipologia_da_estacao(_engine)
    print("tipologia_estacoes:", len(tipologia_estacoes))
    return pd.DataFrame(tipologia_estacoes)


@st.cache_data
def get_estacoes_validadas_rhnr(
    _engine: Engine, df_tipo_estacoes: pd.DataFrame
) -> pd.DataFrame:
    estacoes = retorna_estacoes_validadas_rhnr(_engine)
    estacoes_modificadas = formatar_campo_descricao(estacoes)
    return pd.DataFrame(estacoes_modificadas).merge(
        df_tipo_estacoes, on="Código da Estação", how="left"
    )


@st.cache_data
def get_estacoes_proposta_rhnr(_engine: Engine) -> pd.DataFrame:
    estacoes = retorna_estacoes_rhnr_proposta(_engine)
    estacoes_modificadas = formatar_campo_descricao(estacoes)
    return pd.DataFrame(estacoes_modificadas)


@st.cache_data
def get_objetivos_especificos(_engine: Engine) -> pd.DataFrame:
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
    return pd.DataFrame(result)


@st.cache_data
def join_dataframes_proposta_rhnr(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    df_tipo_estacoes: pd.DataFrame,
    df_filtro: pd.DataFrame,
):
    df = df1.merge(df2, on="Código da Estação", how="left")
    df["RHNR Inicial?"] = df["Código da Estação"].isin(df_filtro["Código da Estação"])
    return df.merge(df_tipo_estacoes, on="Código da Estação", how="left")[
        list(get_args(ColunaTabelaRHNRProposta.__value__))
    ]


# database_url = os.getenv("DATABASE_URL")
database_url = f"sqlite:///{Path.cwd() / 'revisao_rhnr' / 'databases' / 'database.db'}"
# print(database_url)
# st.stop()

if not database_url:
    st.error("DATABASE_URL not set in environment variables.")
    st.stop()

engine = get_db_engine(database_url)
df_tipo_estacoes = get_tipologia_estacoes(engine)
df_rhnr_inicial = get_estacoes_selecao_inicial_rhnr(engine, df_tipo_estacoes)
df_estacoes_validadas = get_estacoes_validadas_rhnr(engine, df_tipo_estacoes)
df_estacoes_rhnr_proposta = get_estacoes_proposta_rhnr(engine)
df_objs_especificos = get_objetivos_especificos(engine)
df_rhnr_proposta = join_dataframes_proposta_rhnr(
    df1=df_estacoes_rhnr_proposta,
    df2=df_objs_especificos,
    df_tipo_estacoes=df_tipo_estacoes,
    df_filtro=df_rhnr_inicial,
)
df_estacoes_potenciais = get_estacoes_potenciais_rhnr(engine, df_tipo_estacoes)
