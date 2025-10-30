"""Script para inserir manualmente estações HidroObserva a jusante de reservatórios nas tabelas do banco de dados."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from revisao_rhnr.databases.alimentacao_tabelas_bd_bases_cplar.constantes import (
    COLS_OBJS_ESPECIFICOS,
)
from revisao_rhnr.databases.models_postgres import (
    EstacaoPropostaRHNR,
    ObjetivoEspecificoEstacaoProposta,
)


def main() -> None:
    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])
    estacoes = [
        37145910,
        37217100,
        37230100,
        37238050,
        37312150,
        37369100,
        37560920,
        37610500,
        38155010,
        38855150,
        48851120,
    ]

    estacoes_atualizar_objetivos = [
        37145910,
        37217100,
        37230100,
        37369100,
        37560920,
        37610500,
        38855150,
        48851120,
    ]

    dict_cols_comum_estacoes = {
        "tipo_estacao": "FD",
        "proposta_operacao_planilha": None,
        "proposta_tipo": None,
        "proposta_integra_rhnr": True,
        "observacao": "Estação HIDROOBSERVA a Jusante de Reservatório",
        "proposta_operacao": None,
    }

    dict_cols_comum_objs_esps = {
        obj_esp: None for obj_esp in COLS_OBJS_ESPECIFICOS.values()
    }

    for codigo in estacoes:
        dict_dados = {"codigo": codigo} | dict_cols_comum_estacoes
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
                print(
                    f"Inserindo estação {codigo} no Tabela revisao_rhnr.obj_espec_estacoes_propostas..."
                )
                objs_esp = dict_cols_comum_objs_esps | {
                    "codigo": codigo,
                    "obj_6d": 1,
                    "tipo_mapeamento": "Manual",
                }
                obj_esp = ObjetivoEspecificoEstacaoProposta(**objs_esp)
                session.add(obj_esp)

            if codigo in estacoes_atualizar_objetivos:
                print(
                    f"Atualizando objetivos específicos da estação {codigo} na tabela revisao_rhnr.obj_espec_estacoes_propostas..."
                )
                objs_esp_atualizado = dict_cols_comum_objs_esps | {
                    "obj_6d": 1,
                    "tipo_mapeamento": "Manual",
                }
                stmt_obj_esp_update = (
                    update(ObjetivoEspecificoEstacaoProposta).where(
                        ObjetivoEspecificoEstacaoProposta.codigo == codigo
                    )
                ).values(**objs_esp_atualizado)
                session.execute(stmt_obj_esp_update)

            session.commit()


if __name__ == "__main__":
    # ============================================================
    # Inserção de Estações HidroObserva a JUSANTE de reservatórios
    # ============================================================
    main()
