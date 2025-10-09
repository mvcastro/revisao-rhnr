from typing import Any, Literal, cast

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from revisao_rhnr.databases.models import (
    Bacia,
    Entidade,
    EstacaoFlu,
    EstacaoPropostaRHNR,
    EstacaoRHNRSelecaoInicial,
    ObjetivoEspecificoEstacaoProposta,
    Operadora,
    Responsavel,
)

type ColunaRHNRInicial = Literal[
    "Código",
    "Nome",
    "Responsável",
    "Operadora",
    "Bacia",
    "Operando",
    "Descrição",
    "Objetivo 1",
    "Objetivo 2",
    "Objetivo 3",
    "Objetivo 4",
    "Objetivo 5",
    "Objetivo 6",
]


type ColunaEstacaoValidadaRHNR = Literal[
    "Código", "Nome", "Responsável", "Operadora", "Bacia", "Operando", "Descrição"
]


type ColunaRHNRProposta = Literal[
    "Código da Estação",
    "Nome",
    "Responsável",
    "Operadora",
    "Bacia",
    "Operando",
    "Descrição",
    "Tipologia Atual",
    "RHNR Inicial?",
    "Ação Proposta",
    "Tipologia Proposta",
    "Integra RHNR?",
    "Objs. Específicos",
]


def retorna_estacoes_rhnr_selecao_inicial(
    engine: Engine,
) -> list[dict[ColunaRHNRInicial, Any]]:
    query_responsavel = (
        select(Responsavel.codigo_estacao, Entidade.sigla)
        .where(Responsavel.responsavel_codigo == Entidade.codigo)
        .subquery()
    )

    query_operadora = (
        select(Operadora.codigo_estacao, Entidade.sigla)
        .where(Operadora.operadora_codigo == Entidade.codigo)
        .subquery()
    )

    with Session(engine) as session:
        response = session.execute(
            select(
                EstacaoFlu.codigo.label("Código da Estação"),
                EstacaoFlu.nome.label("Nome"),
                query_responsavel.c.sigla.label("Responsável"),
                query_operadora.c.sigla.label("Operadora"),
                Bacia.nome.label("Bacia"),
                EstacaoFlu.operando.label("Operando"),
                EstacaoFlu.descricao.label("Descrição"),
                EstacaoRHNRSelecaoInicial.objetivo1.label("Objetivo 1"),
                EstacaoRHNRSelecaoInicial.objetivo2.label("Objetivo 2"),
                EstacaoRHNRSelecaoInicial.objetivo3.label("Objetivo 3"),
                EstacaoRHNRSelecaoInicial.objetivo4.label("Objetivo 4"),
                EstacaoRHNRSelecaoInicial.objetivo5.label("Objetivo 5"),
                EstacaoRHNRSelecaoInicial.objetivo6.label("Objetivo 6"),
            )
            .where(
                EstacaoFlu.codigo == EstacaoRHNRSelecaoInicial.codigo,
                EstacaoFlu.bacia_codigo == Bacia.codigo,
            )
            .join(
                target=query_responsavel,
                onclause=EstacaoFlu.codigo == query_responsavel.c.codigo_estacao,
                isouter=True,
            )
            .join(
                target=query_operadora,
                onclause=EstacaoFlu.codigo == query_operadora.c.codigo_estacao,
                isouter=True,
            )
        )

        result = [row._asdict() for row in response]
    return cast(list[dict[ColunaRHNRInicial, Any]], result)


def retorna_estacoes_validadas_rhnr(
    engine: Engine,
) -> list[dict[ColunaEstacaoValidadaRHNR, Any]]:
    query_responsavel = (
        select(Responsavel.codigo_estacao, Entidade.sigla)
        .where(Responsavel.responsavel_codigo == Entidade.codigo)
        .subquery()
    )

    query_operadora = (
        select(Operadora.codigo_estacao, Entidade.sigla)
        .where(Operadora.operadora_codigo == Entidade.codigo)
        .subquery()
    )

    with Session(engine) as session:
        response = session.execute(
            select(
                EstacaoFlu.codigo.label("Código da Estação"),
                EstacaoFlu.nome.label("Nome"),
                query_responsavel.c.sigla.label("Responsável"),
                query_operadora.c.sigla.label("Operadora"),
                Bacia.nome.label("Bacia"),
                EstacaoFlu.operando.label("Operando"),
                EstacaoFlu.descricao.label("Descrição"),
            )
            .join(
                Bacia,
                EstacaoFlu.bacia_codigo == Bacia.codigo,
            )
            .join(
                target=query_responsavel,
                onclause=EstacaoFlu.codigo == query_responsavel.c.codigo_estacao,
                isouter=True,
            )
            .join(
                target=query_operadora,
                onclause=EstacaoFlu.codigo == query_operadora.c.codigo_estacao,
                isouter=True,
            )
            .where(EstacaoFlu.descricao.like("%RHNR%"))
        )

        result = [row._asdict() for row in response]
    return cast(list[dict[ColunaEstacaoValidadaRHNR, Any]], result)


def retorna_estacoes_rhnr_proposta(engine) -> list[dict[ColunaRHNRProposta, Any]]:
    query_responsavel = (
        select(Responsavel.codigo_estacao, Entidade.sigla)
        .where(Responsavel.responsavel_codigo == Entidade.codigo)
        .subquery()
    )

    query_operadora = (
        select(Operadora.codigo_estacao, Entidade.sigla)
        .where(Operadora.operadora_codigo == Entidade.codigo)
        .subquery()
    )

    with Session(engine) as session:
        response = session.execute(
            select(
                EstacaoPropostaRHNR.codigo.label("Código da Estação"),
                EstacaoFlu.nome.label("Nome"),
                query_responsavel.c.sigla.label("Responsável"),
                query_operadora.c.sigla.label("Operadora"),
                Bacia.nome.label("Bacia"),
                EstacaoFlu.operando.label("Operando"),
                EstacaoFlu.descricao.label("Descrição"),
                EstacaoPropostaRHNR.tipo_estacao.label("Tipologia Atual"),
                EstacaoPropostaRHNR.proposta_tipo.label("Tipologia Proposta"),
                EstacaoPropostaRHNR.proposta_integra_rhnr.label("Integra RHNR?"),
                EstacaoPropostaRHNR.proposta_operacao.label("Ação Proposta"),
            )
            .where(
                EstacaoFlu.codigo == EstacaoPropostaRHNR.codigo,
                EstacaoFlu.bacia_codigo == Bacia.codigo,
            )
            .join(
                target=query_responsavel,
                onclause=EstacaoFlu.codigo == query_responsavel.c.codigo_estacao,
                isouter=True,
            )
            .join(
                target=query_operadora,
                onclause=EstacaoFlu.codigo == query_operadora.c.codigo_estacao,
                isouter=True,
            )
        )

        result = [row._asdict() for row in response]

    return cast(list[dict[ColunaRHNRProposta, Any]], result)


def retorna_objetivos_especificos(engine: Engine) -> list[dict]:
    with Session(engine) as session:
        response = (
            session.execute(select(ObjetivoEspecificoEstacaoProposta)).scalars().all()
        )

    return [row.to_dict() for row in response]
