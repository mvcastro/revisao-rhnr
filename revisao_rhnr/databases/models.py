import os
from datetime import date
from typing import Literal

from dotenv import load_dotenv
from sqlalchemy import SmallInteger, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

TipoHidroRef = Literal["Área de Drenagem", "Nome do Rio", "Desmias Estações"]


class Base(DeclarativeBase): ...


class EstacaoFlu(Base):
    __tablename__ = "estacao_flu"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    codigo_adicional: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    altitude: Mapped[float]
    area_drenagem: Mapped[float | None]
    bacia_codigo: Mapped[int]
    subbacia_codigo: Mapped[int]
    rio_codigo: Mapped[int | None]
    estado_codigo: Mapped[int]
    municipio_codigo: Mapped[int]
    ultima_atualizacao: Mapped[date]
    operando: Mapped[int]
    descricao: Mapped[str]
    historico: Mapped[str]


class Bacia(Base):
    __tablename__ = "bacia"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]


class Entidade(Base):
    __tablename__ = "entidade"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    sigla: Mapped[str]
    nome: Mapped[str]


class Responsavel(Base):
    __tablename__ = "responsavel"

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    responsavel_codigo: Mapped[int]
    responsavel_unidade: Mapped[int]
    responsavel_jurisdicao: Mapped[int]


class Operadora(Base):
    __tablename__ = "operadora"

    codigo_estacao: Mapped[int] = mapped_column(primary_key=True)
    operadora_codigo: Mapped[int]
    operadora_unidade: Mapped[int]
    operadora_subunidade: Mapped[int]


class EstacaoRHNRSelecaoInicial(Base):
    __tablename__ = "estacoes_rhnr_selecao_inicial"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    objetivo1: Mapped[int] = mapped_column(SmallInteger)
    objetivo2: Mapped[int] = mapped_column(SmallInteger)
    objetivo3: Mapped[int] = mapped_column(SmallInteger)
    objetivo4: Mapped[int] = mapped_column(SmallInteger)
    objetivo5: Mapped[int] = mapped_column(SmallInteger)
    objetivo6: Mapped[int] = mapped_column(SmallInteger)


class EstacaoPropostaRHNR(Base):
    __tablename__ = "estacoes_proposta_rhnr"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    tipo_estacao: Mapped[str] = mapped_column(String(5), nullable=False)
    proposta_operacao_temp: Mapped[str] = mapped_column(nullable=True)
    proposta_tipo: Mapped[str] = mapped_column(String(5), nullable=True)
    proposta_integra_rhnr: Mapped[bool] = mapped_column(nullable=True)
    observacao: Mapped[str] = mapped_column(nullable=True)
    proposta_operacao: Mapped[str] = mapped_column(nullable=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ObjetivoEspecificoEstacaoProposta(Base):
    __tablename__ = "obj_espec_estacoes_propostas"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    obj_1a: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_1b: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_2a: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_2b: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_2c: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_3a: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_3b: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_4a: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_4b: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_4c: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_4d: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_5a: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_5b: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_6a: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_6b: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_6c: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_6d: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_6e: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    obj_6f: Mapped[int] = mapped_column(SmallInteger, nullable=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class EstacaoRedundante(Base):
    __tablename__ = "estacoes_redundantes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[int] = mapped_column(nullable=False)
    codigo_redundante: Mapped[int] = mapped_column(nullable=False)
    tipo_estacao: Mapped[str] = mapped_column(String(10), nullable=False)


if __name__ == "__main__":
    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])
    Base.metadata.create_all(bind=engine)
