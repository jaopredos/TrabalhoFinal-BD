import os
from dotenv import load_dotenv
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# URL de conexão com o seu banco PostgreSQL.
# Formato: "postgresql://usuario:senha@host:porta/nome_do_banco"
password = os.getenv("DB_PASSWORD")
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{password}@127.0.0.1:5432/postgres"

# Cria a engine de conexão
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria uma fábrica de sessões. Cada instância de SessionLocal será uma sessão com o banco.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Uma classe base que nossos modelos ORM irão herdar
Base = declarative_base()

# Dependência para ser usada nos endpoints da API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()