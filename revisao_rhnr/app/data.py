import os
from enum import StrEnum
from typing import get_args

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

from revisao_rhnr.databases.database_access import (
    ColunaRHNRInicial,
    ColunaRHNRProposta,
    retorna_estacoes_rhnr_proposta,
    retorna_estacoes_rhnr_selecao_inicial,
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


@st.cache_resource
def get_db_engine(url: str):
    return create_engine(url)


@st.cache_data
def get_estacoes_selecao_inicial_rhnr(_engine: Engine):
    estacoes = retorna_estacoes_rhnr_selecao_inicial(_engine)
    return estacoes


@st.cache_data
def get_estacoes_proposta_rhnr(_engine: Engine):
    estacoes = retorna_estacoes_rhnr_proposta(_engine)
    return estacoes


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
        [est["Código"] for est in filtro]
    )

    return df


database_url = os.getenv("DATABASE_URL")
if not database_url:
    st.error("DATABASE_URL not set in environment variables.")
    st.stop()

engine = get_db_engine(database_url)
dict_rhrnr_inicial = get_estacoes_selecao_inicial_rhnr(engine)
df_rhnr_inicial = pd.DataFrame(dict_rhrnr_inicial)
estacoes_rhnr_proposta = get_estacoes_proposta_rhnr(engine)
objetivos_especificos = get_objetivos_especificos(engine)
df_rhnr_proposta = join_dataframes_proposta_rhnr(
    pd.DataFrame(estacoes_rhnr_proposta),
    pd.DataFrame(objetivos_especificos),
    dict_rhrnr_inicial,
)
