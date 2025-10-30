"Estações levantadas manualmente na Revisão RHNR pelo Flávio Troger"

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from revisao_rhnr.databases.alimentacao_tabelas_bd_bases_cplar.constantes import (
    COLS_OBJS_ESPECIFICOS,
)
from revisao_rhnr.databases.models_postgres import (
    EstacaoPropostaRHNR,
    ObjetivoEspecificoEstacaoProposta,
)


def retorna_tipologia_estacao(row: pd.Series) -> str:
    """Retorna a tipologia da estação com base nas colunas de tipologia da planilha do Excel."""
    tipologia = []
    if row["Escala"] == "Sim":
        tipologia.append("F")
    if row["Descarga líquida"] == "Sim":
        tipologia.append("D")
    if row["Qualidade da água"] == "Sim":
        tipologia.append("Q")
    if row["Sedimentos"] == "Sim":
        tipologia.append("S")
    if row["Telemétrica"] == "Sim":
        tipologia.append("T")

    if not tipologia:
        raise ValueError(f"Tipologia inválida para a estação {row['Código']}")

    return "".join(tipologia)


def main():
    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])
    folder = "C:/Users/marco.goncalves/Downloads"
    filename = "RedeFLU-ANA_Poderia-ser-RHNR.xlsx"

    dict_cols_comum_estacoes = {
        "tipo_estacao": None,
        "proposta_operacao_planilha": None,
        "proposta_tipo": None,
        "proposta_integra_rhnr": True,
        "observacao": "Estação levantada manualmente pelo Flávio Troger",
        "proposta_operacao": None,
    }

    dict_cols_comum_objs_esps = {
        obj_esp: None for obj_esp in COLS_OBJS_ESPECIFICOS.values()
    }

    df = pd.read_excel(io=f"{folder}/{filename}")

    for _, row in df.iterrows():
        tipologia = retorna_tipologia_estacao(row)
        codigo = row["Código-Estação"]

        dict_dados = dict_cols_comum_estacoes | {
            "codigo": codigo,
            "tipo_estacao": tipologia,
        }
        with Session(engine) as session:
            stmt_prop = select(EstacaoPropostaRHNR).where(
                EstacaoPropostaRHNR.codigo == codigo
            )
            estacao_prop_existente = session.execute(stmt_prop).scalar_one_or_none()
            if not estacao_prop_existente:
                print(
                    f"Inserindo estação {codigo} no Tabela revisao_rhnr.estacoes_proposta_rhnr..."
                )
                estacao = EstacaoPropostaRHNR(**dict_dados)
                session.add(estacao)

            stmt_obj_esp = select(ObjetivoEspecificoEstacaoProposta).where(
                ObjetivoEspecificoEstacaoProposta.codigo == codigo
            )
            obj_esp_existente = session.execute(stmt_obj_esp).scalar_one_or_none()
            if not obj_esp_existente:
                objs_especificos = row["Objetivos Especificos"].split(",")
                dict_objs_especificos = {
                    f"obj_{obj.strip()}": 1 for obj in objs_especificos
                }
                print(
                    f"Inserindo estação {codigo} no Tabela revisao_rhnr.obj_espec_estacoes_propostas..."
                )
                objs_esp = (
                    dict_cols_comum_objs_esps
                    | {
                        "codigo": codigo,
                        "tipo_mapeamento": "Manual",
                    }
                    | dict_objs_especificos
                )
                obj_esp = ObjetivoEspecificoEstacaoProposta(**objs_esp)
                session.add(obj_esp)

            session.commit()


if __name__ == "__main__":
    main()
