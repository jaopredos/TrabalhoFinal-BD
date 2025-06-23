import os
import sqlalchemy
from google.cloud.sql.connector import Connector

# Carrega as configurações do ambiente
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")

# Inicializa o conector globalmente
connector = Connector()

# Função auxiliar para o SQLAlchemy
def get_db_connection():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn

# Cria o pool de conexões que será importado por outros arquivos
# Este é o objeto que suas rotas irão usar
db_pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=get_db_connection,
)