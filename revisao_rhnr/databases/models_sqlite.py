from datetime import date
from pathlib import Path

from sqlalchemy import ForeignKey, SmallInteger, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class EstacaoFlu(Base):
    __tablename__ = "estacao_flu"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    codigo_adicional: Mapped[str | None]
    latitude: Mapped[float]
    longitude: Mapped[float]
    altitude: Mapped[float | None]
    area_drenagem: Mapped[float | None]
    bacia_codigo: Mapped[int] = mapped_column(ForeignKey("bacia.codigo"))
    subbacia_codigo: Mapped[int] = mapped_column(ForeignKey("subbacia.codigo"))
    estado_codigo: Mapped[int] = mapped_column(ForeignKey("estado.codigo"))
    municipio_codigo: Mapped[int] = mapped_column(ForeignKey("municipio.codigo"))
    ultima_atualizacao: Mapped[date]
    operando: Mapped[int]
    descricao: Mapped[str]
    historico: Mapped[str]


class Entidade(Base):
    __tablename__ = "entidade"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    sigla: Mapped[str]


class Bacia(Base):
    __tablename__ = "bacia"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]


class SubBacia(Base):
    __tablename__ = "subbacia"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    jurisdicao: Mapped[int | None] = mapped_column(
        ForeignKey("entidade.codigo"), nullable=True
    )
    bacia_codigo: Mapped[int] = mapped_column(ForeignKey("bacia.codigo"))


class Rio(Base):
    __tablename__ = "rio"

    codigo_estacao: Mapped[int] = mapped_column(
        ForeignKey("estacao_flu.codigo"), primary_key=True
    )
    nome: Mapped[str]
    jurisdicao: Mapped[int] = mapped_column(ForeignKey("entidade.codigo"), nullable=True)
    bacia_codigo: Mapped[int] = mapped_column(ForeignKey("bacia.codigo"))
    subbacia_codigo: Mapped[int] = mapped_column(ForeignKey("subbacia.codigo"))


class Estado(Base):
    __tablename__ = "estado"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    codigo_ibge: Mapped[int]
    sigla: Mapped[str]
    nome: Mapped[str]


class Municipio(Base):
    __tablename__ = "municipio"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    codigo_ibge: Mapped[int]
    nome: Mapped[str]
    estado_codigo: Mapped[int] = mapped_column(ForeignKey("estado.codigo"))


class Responsavel(Base):
    __tablename__ = "responsavel"

    codigo_estacao: Mapped[int] = mapped_column(
        ForeignKey("estacao_flu.codigo"), primary_key=True
    )
    responsavel_codigo: Mapped[int] = mapped_column(ForeignKey("entidade.codigo"))
    responsavel_unidade: Mapped[int | None]
    responsavel_jurisdicao: Mapped[int | None]


class Operadora(Base):
    __tablename__ = "operadora"

    codigo_estacao: Mapped[int] = mapped_column(
        ForeignKey("estacao_flu.codigo"), primary_key=True
    )
    operadora_codigo: Mapped[int] = mapped_column(ForeignKey("entidade.codigo"))
    operadora_unidade: Mapped[int | None]
    operadora_subunidade: Mapped[int | None]


class TipoEstacaoFlu(Base):
    __tablename__ = "tipo_estacao_flu"

    codigo_estacao: Mapped[int] = mapped_column(
        ForeignKey("estacao_flu.codigo"), primary_key=True
    )
    escala: Mapped[bool]
    registrador_nivel: Mapped[bool]
    descarga_liquida: Mapped[bool]
    sedimentos: Mapped[bool]
    qualidade_agua: Mapped[bool]
    telemetrica: Mapped[bool]


class EstacaoRHNRSelecaoInicial(Base):
    __tablename__ = "estacoes_rhnr_selecao_inicial"

    codigo: Mapped[int] = mapped_column(
        ForeignKey("estacao_flu.codigo"), primary_key=True
    )
    objetivo1: Mapped[int] = mapped_column(SmallInteger)
    objetivo2: Mapped[int] = mapped_column(SmallInteger)
    objetivo3: Mapped[int] = mapped_column(SmallInteger)
    objetivo4: Mapped[int] = mapped_column(SmallInteger)
    objetivo5: Mapped[int] = mapped_column(SmallInteger)
    objetivo6: Mapped[int] = mapped_column(SmallInteger)


class EstacaoPropostaRHNR(Base):
    __tablename__ = "estacoes_proposta_rhnr"

    codigo: Mapped[int] = mapped_column(
        ForeignKey("estacao_flu.codigo"), primary_key=True
    )
    tipo_estacao: Mapped[str] = mapped_column(String(5), nullable=False)
    proposta_operacao_planilha: Mapped[str] = mapped_column(nullable=True)
    proposta_tipo: Mapped[str] = mapped_column(String(5), nullable=True)
    proposta_integra_rhnr: Mapped[bool] = mapped_column(nullable=True)
    observacao: Mapped[str] = mapped_column(nullable=True)
    proposta_operacao: Mapped[str] = mapped_column(nullable=True)


class ObjetivoEspecificoEstacaoProposta(Base):
    __tablename__ = "obj_espec_estacoes_propostas"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    obj_1a: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_1b: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_2a: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_2b: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_2c: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_3a: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_3b: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_4a: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_4b: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_4c: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_4d: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_5a: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_5b: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_6a: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_6b: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_6c: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_6d: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_6e: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    obj_6f: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    tipo_mapeamento: Mapped[str] = mapped_column(nullable=False)


class EstacaoRedundante(Base):
    __tablename__ = "estacoes_redundantes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[int] = mapped_column(
        ForeignKey("estacao_flu.codigo"), nullable=False
    )
    codigo_redundante: Mapped[int] = mapped_column(nullable=False)
    tipo_estacao: Mapped[str] = mapped_column(String(10), nullable=False)


if __name__ == "__main__":
    url = f"sqlite:///{Path(__file__).parent / 'database.db'}"
    engine = create_engine(url=url)
    Base.metadata.create_all(bind=engine)
