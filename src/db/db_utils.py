import psycopg2

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from gen_ai_project_template.src.utils.fun_utils import seguimiento_funciones, msg_succ, msg_warn, msg_error

@seguimiento_funciones
def fun_connection_params(host, port, database, user, password):
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

@seguimiento_funciones
def get_engine(conn_str: str) -> Engine:
    return create_engine(conn_str, echo=False, future=True)

def fetch_all(engine: Engine, query: str, params: dict = None) -> list[dict]:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            rows = [dict(row) for row in result.mappings()]
            return rows
    except SQLAlchemyError as e:
        print(f"Error en fetch_all: {e}")
        return []

def fetch_one(engine: Engine, query: str, params: dict = None) -> dict | None:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            row = result.mappings().first()
            return dict(row) if row else None
    except SQLAlchemyError as e:
        print(f"Error en fetch_one: {e}")
        return None


@seguimiento_funciones
def execute_query(engine: Engine, query: str, params: dict = None) -> None:
    """
    Ejecuta un INSERT/UPDATE/DELETE.
    """
    try:
        with engine.begin() as conn:  # begin -> asegura commit/rollback
            conn.execute(text(query), params or {})
        print("Query ejecutada con éxito")
    except SQLAlchemyError as e:
        print(f"Error en execute_query: {e}")