import os
from inspect import isclass
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from revisao_rhnr.databases import models_postgres, models_sqlite


def create_engine_bases_cplar():
    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])
    return engine


def create_local_engine():
    url = f"sqlite:///{Path(__file__).parent / 'database.db'}"
    engine = create_engine(url=url)
    return engine


def get_classes_from_module(module, classtype):
    classes = {}
    for classe in dir(module):
        if not isclass(getattr(module, classe)):
            continue
        if issubclass(getattr(module, classe), classtype):
            classes[classe] = getattr(module, classe)

    return classes


def get_data_from_base_class(engine_bases_cplar, classe):
    with Session(engine_bases_cplar) as session:
        instances = session.execute(select(classe)).scalars().all()
        return instances


def migra_dados_dos_bancos():
    classes = get_classes_from_module(models_postgres, models_postgres.Base)

    engine_bases_cplar = create_engine_bases_cplar()
    engine_local = create_local_engine()

    for nome_classe, classe in classes.items():
        instances = get_data_from_base_class(engine_bases_cplar, classe)

        new_class = getattr(models_sqlite, nome_classe)
        new_instances = [new_class(**instance.to_dict()) for instance in instances]
        with Session(engine_local) as local_session:
            local_session.add_all(new_instances)
            local_session.commit()


if __name__ == "__main__":
    migra_dados_dos_bancos()
