import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from revisao_rhnr.databases.models import EstacaoRedundante


def alimenta_estacoes_rhnr_selecao_inicial(engine: Engine):
    folder_path = (
        r"\\agencia\ana\SGH\CPLAR\RHNR\Mapas\Acessórios\Resultado Final 23092016"
    )
    file_path = "Estacoes_objetivos_URs_Selecionadas_865estações.xls"

    colunas = {
        "CODIGO": "codigo",
        "OBJ1": "objetivo1",
        "OBJ2": "objetivo2",
        "OBJ3": "objetivo3",
        "OBJ4": "objetivo4",
        "OBJ5": "objetivo5",
        "OBJ6": "objetivo6",
    }
    df = pd.read_excel(os.path.join(folder_path, file_path))[colunas.keys()].rename(
        columns=colunas
    )
    df.to_sql(
        name="estacoes_rhnr_selecao_inicial",
        con=engine,
        if_exists="append",
        schema="revisao_rhnr",
        index=False,
    )


def retorna_dataframe_da_tabela_excel(
    file_path: str,
    colunas: dict[str, str],
    skip_rows: int,
    sheet_name: str | None = None,
) -> pd.DataFrame:
    folder_path = "C:/Users/marco.goncalves/Downloads/Revisao_RHNR"

    df = pd.read_excel(
        os.path.join(folder_path, file_path),
        skiprows=skip_rows,
        usecols=list(colunas.keys()),
        na_values=[
            "-",
            "--",
            "---",
            " --",
            "",
            "NOVA",
            "***",
            "NOVA ESTAÇÃO",
            "99999999",
        ],
        sheet_name=sheet_name if sheet_name else 0,
    ).rename(columns=colunas)

    return df


def alimenta_estacoes_proposta_rhnr(engine: Engine, dataframe: pd.DataFrame) -> None:
    # Tabela revisao_rhnr.estacoes_proposta_rhnr
    colunas_tabela_estacoes_proposta = [
        "codigo",
        "tipo_estacao",
        "proposta_operacao",
        "proposta_tipo",
        "proposta_integra_rhnr",
        "observacao",
    ]

    renomeia_boolean = {
        "Não": False,
        "Sim": True,
    }

    df = (
        dataframe[colunas_tabela_estacoes_proposta][~dataframe.codigo.isna()]
        .copy()
        .replace({"proposta_integra_rhnr": renomeia_boolean})
    )
    df.to_sql(
        name="estacoes_proposta_rhnr",
        con=engine,
        if_exists="append",
        schema="revisao_rhnr",
        index=False,
    )


def alimenta_estacoes_redundantes(engine: Engine, dataframe: pd.DataFrame) -> None:
    # Tabela revisao_rhnr.estacoes_redundantes
    colunas_tabela_estacoes_redundantes = ["codigo", "redundancia"]

    table_rows: list[EstacaoRedundante] = []
    for _, row in dataframe[colunas_tabela_estacoes_redundantes].iterrows():
        if pd.isna(row.codigo) or pd.isna(row.redundancia):
            continue

        print(f"Linha: {row.redundancia}")
        for info_redundancia in row.redundancia.split("\n"):
            print(f"{info_redundancia=}")
            codigo_redundante, tipo_estacao = info_redundancia.split(" - ")
            print(
                f"{codigo_redundante=}, {tipo_estacao=}, tamanho={len(tipo_estacao.strip())}"
            )
            table_rows.append(
                EstacaoRedundante(
                    codigo=int(row.codigo),
                    codigo_redundante=int(codigo_redundante.strip()),
                    tipo_estacao=tipo_estacao.split(" ")[0],
                )
            )
    with Session(engine) as session:
        session.add_all(table_rows)
        session.commit()


def alimenta_objetivos_especificos(engine: Engine, dataframe: pd.DataFrame) -> None:
    # Tabela revisao_rhnr.obj_espec_estacoes_propostas
    colunas_tabela_objs_especificos = [
        "codigo",
        "obj_1a",
        "obj_1b",
        "obj_2a",
        "obj_2b",
        "obj_2c",
        "obj_3a",
        "obj_3b",
        "obj_4a",
        "obj_4b",
        "obj_4c",
        "obj_4d",
        "obj_5a",
        "obj_5b",
        "obj_6a",
        "obj_6b",
        "obj_6c",
        "obj_6d",
        "obj_6e",
        "obj_6f",
    ]

    df = dataframe[colunas_tabela_objs_especificos][~dataframe.codigo.isna()].copy()
    df.to_sql(
        name="obj_espec_estacoes_propostas",
        con=engine,
        if_exists="append",
        schema="revisao_rhnr",
        index=False,
    )


if __name__ == "__main__":
    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])
    # alimenta_estacoes_rhnr_selecao_inicial(engine)

    # Colunas Tabela São Franciscio - Sub-médio e baixo
    # colunas = {
    #     "Código": "codigo",
    #     "Tipo": "tipo_estacao",
    #     "Redundância\n(estações próximas)": "redundancia",
    #     "1a": "obj_1a",
    #     "1b": "obj_1b",
    #     "2a": "obj_2a",
    #     "2b": "obj_2b",
    #     "2c": "obj_2c",
    #     "3a": "obj_3a",
    #     "3b": "obj_3b",
    #     "4a": "obj_4a",
    #     "4b": "obj_4b",
    #     "4c": "obj_4c",
    #     "4d": "obj_4d",
    #     "5a": "obj_5a",
    #     "5b": "obj_5b",
    #     "6a": "obj_6a",
    #     "6b": "obj_6b",
    #     "6c": "obj_6c",
    #     "6d": "obj_6d",
    #     "6e": "obj_6e",
    #     "6f": "obj_6f",
    #     "Operação \nda Estação": "proposta_operacao",
    #     "Tipo\nSugerido": "proposta_tipo",
    #     "Integrar \na RHNR": "proposta_integra_rhnr",
    #     "Observações sobre a Proposta": "observacao",
    # }
    # df = retorna_dataframe_da_tabela_excel(
    #     "Revisão rede São Francisco_sub-médio e baixo.xlsx",
    #     colunas=colunas,
    #     skip_rows=3
    # )

    # Colunas Tabela Maranhão Piauí
    # colunas = {
    #     "Código": "codigo",
    #     "Tipologia atual": "tipo_estacao",
    #     "1a": "obj_1a",
    #     "1b": "obj_1b",
    #     "2a": "obj_2a",
    #     "2b": "obj_2b",
    #     "2c": "obj_2c",
    #     "3a": "obj_3a",
    #     "3b": "obj_3b",
    #     "4a": "obj_4a",
    #     "4b": "obj_4b",
    #     "4c": "obj_4c",
    #     "4d": "obj_4d",
    #     "5a": "obj_5a",
    #     "5b": "obj_5b",
    #     "6a": "obj_6a",
    #     "6b": "obj_6b",
    #     "6c": "obj_6c",
    #     "6d": "obj_6d",
    #     "6e": "obj_6e",
    #     "6f": "obj_6f",
    #     "Proposição": "proposta_operacao",
    #     "Tipologia": "proposta_tipo",
    #     "RHNR": "proposta_integra_rhnr",
    #     "Análise/justificativa/observações": "observacao",
    # }
    # df = retorna_dataframe_da_tabela_excel(
    #     "Revisão rede Maranhão e Piauí_SGB_RETE.xlsx",
    #     colunas=colunas,
    #     skip_rows=1,
    #     sheet_name='Rede atual'
    # )

    # Colunas Tabela Ceará
    # colunas = {
    #     "Código": "codigo",
    #     "Tipologia Atual": "tipo_estacao",
    #     "1a": "obj_1a",
    #     "1b": "obj_1b",
    #     "2a": "obj_2a",
    #     "2b": "obj_2b",
    #     "2c": "obj_2c",
    #     "3a": "obj_3a",
    #     "3b": "obj_3b",
    #     "4a": "obj_4a",
    #     "4b": "obj_4b",
    #     "4c": "obj_4c",
    #     "4d": "obj_4d",
    #     "5a": "obj_5a",
    #     "5b": "obj_5b",
    #     "6a": "obj_6a",
    #     "6b": "obj_6b",
    #     "6c": "obj_6c",
    #     "6d": "obj_6d",
    #     "6e": "obj_6e",
    #     "6f": "obj_6f",
    #     "Proposição": "proposta_operacao",
    #     "Tipologia Proposta": "proposta_tipo",
    #     "Proposta RHNR": "proposta_integra_rhnr",
    #     "Sugestão": "observacao",
    # }
    # df = retorna_dataframe_da_tabela_excel(
    #     "Revisão rede Ceará_SGB_REFO.xlsx",
    #     colunas=colunas,
    #     skip_rows=1,
    # )

    # Colunas Tabela Rio Grande do Sul
    # colunas = {
    #     "Estação - Código": "codigo",
    #     "Tipologia Atual": "tipo_estacao",
    #     "1a": "obj_1a",
    #     "1b": "obj_1b",
    #     "2a": "obj_2a",
    #     "2b": "obj_2b",
    #     "2c": "obj_2c",
    #     "3a": "obj_3a",
    #     "3b": "obj_3b",
    #     "4a": "obj_4a",
    #     "4b": "obj_4b",
    #     "4c": "obj_4c",
    #     "4d": "obj_4d",
    #     "5a": "obj_5a",
    #     "5b": "obj_5b",
    #     "6a": "obj_6a",
    #     "6b": "obj_6b",
    #     "6c": "obj_6c",
    #     "6d": "obj_6d",
    #     "6e": "obj_6e",
    #     "6f": "obj_6f",
    #     "Ação de Médio/ Longo Prazos (2026 ou após)": "proposta_operacao",
    #     "Tipologia a ser mantida": "proposta_tipo",
    #     "Integrar à RHNR": "proposta_integra_rhnr",
    #     "Observações": "observacao",
    # }
    # df = retorna_dataframe_da_tabela_excel(
    #     "Revisão rede Rio Grande do Sul.xlsx",
    #     colunas=colunas,
    #     skip_rows=2,
    # )

    # Colunas Tabela Paraíba do Sul
    # colunas = {
    #     "Código": "codigo",
    #     "Tipo": "tipo_estacao",
    #     "1a": "obj_1a",
    #     "1b": "obj_1b",
    #     "2a": "obj_2a",
    #     "2b": "obj_2b",
    #     "2c": "obj_2c",
    #     "3a": "obj_3a",
    #     "3b": "obj_3b",
    #     "4a": "obj_4a",
    #     "4b": "obj_4b",
    #     "4c": "obj_4c",
    #     "4d": "obj_4d",
    #     "5a": "obj_5a",
    #     "5b": "obj_5b",
    #     "6a": "obj_6a",
    #     "6b": "obj_6b",
    #     "6c": "obj_6c",
    #     "6d": "obj_6d",
    #     "6e": "obj_6e",
    #     "6f": "obj_6f",
    #     "Estação": "proposta_operacao",
    #     # "Tipologia a ser mantida": "proposta_tipo",
    #     "RHNR": "proposta_integra_rhnr",
    #     "Observações": "observacao",
    # }
    # df = retorna_dataframe_da_tabela_excel(
    #     "Revisão rede Paraíba do Sul.xlsx",
    #     colunas=colunas,
    #     skip_rows=3,
    # )
    # df['proposta_tipo'] = None

    # Colunas Tabela PCJ/Tietê/Grande/Paranapanema
    # colunas = {
    #     "Código": "codigo",
    #     "Tipo": "tipo_estacao",
    #     "1a": "obj_1a",
    #     "1b": "obj_1b",
    #     "2a": "obj_2a",
    #     "2b": "obj_2b",
    #     "2c": "obj_2c",
    #     "3a": "obj_3a",
    #     "3b": "obj_3b",
    #     "4a": "obj_4a",
    #     "4b": "obj_4b",
    #     "4c": "obj_4c",
    #     "4d": "obj_4d",
    #     "5a": "obj_5a",
    #     "5b": "obj_5b",
    #     "6a": "obj_6a",
    #     "6b": "obj_6b",
    #     "6c": "obj_6c",
    #     "6d": "obj_6d",
    #     "6e": "obj_6e",
    #     "6f": "obj_6f",
    #     "Estação": "proposta_operacao",
    #     # "Tipologia a ser mantida": "proposta_tipo",
    #     "RHNR": "proposta_integra_rhnr",
    #     "Observações": "observacao",
    # }
    # df = retorna_dataframe_da_tabela_excel(
    #     "Revisão rede PCJ_Tiete_Grande_Paranapanema.xlsx",
    #     colunas=colunas,
    #     skip_rows=3,
    # )
    # df['proposta_tipo'] = None
    # objs_cols = [col for col in df.columns if 'obj' in col]
    # for col in  objs_cols:
    #     df[col] = df[col].replace({2.0: 1.0})

    # Colunas Tabela RN / PB / PE / AL
    colunas = {
        "Código": "codigo",
        "Tipo Atual": "tipo_estacao",
        "Proposição": "proposta_operacao",
        "Tipo Sugerido": "proposta_tipo",
        "RHNR": "proposta_integra_rhnr",
        "Operação 2022": "observacao",
    }
    df = retorna_dataframe_da_tabela_excel(
        "Revisão rede RN_PB_PE_AL_SGB_Recife.xlsx",
        colunas=colunas,
        skip_rows=1,
        sheet_name="Geral",
    )
    df_filter = df[(~df.tipo_estacao.isin(['P', 'PT', 'T'])) & (~df.codigo.isna())]

    alimenta_estacoes_proposta_rhnr(engine, df_filter)
    # alimenta_estacoes_redundantes(engine, df)
    # alimenta_objetivos_especificos(engine, df)
