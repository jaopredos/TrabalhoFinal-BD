import os
import sqlalchemy
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Carrega as configurações do ambiente para conexão direta
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")  # Ex: 34.123.45.67 (IP público da instância)
DB_PORT = os.environ.get("DB_PORT", 5432) # Porta padrão do PostgreSQL é 5432

# Verifica se todas as variáveis necessárias foram carregadas
if not all([DB_USER, DB_PASS, DB_NAME, DB_HOST]):
    raise ValueError("Uma ou mais variáveis de ambiente do banco de dados não foram definidas.")

# Monta a string de conexão (DSN - Data Source Name)
# Usando psycopg2 (recomendado):
db_url = sqlalchemy.URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

# Se preferir usar pg8000:
# db_url = sqlalchemy.URL.create(
#     drivername="postgresql+pg8000",
#     username=DB_USER,
#     password=DB_PASS,
#     host=DB_HOST,
#     port=DB_PORT,
#     database=DB_NAME,
# )


# Cria o pool de conexões que será importado por outros arquivos.
# Este é o objeto que suas rotas irão usar.
# A opção `pool_size` e `max_overflow` são boas práticas para gerenciar conexões.
db_pool = sqlalchemy.create_engine(
    db_url,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,
)

# Para testar a conexão imediatamente (opcional, mas recomendado)
try:
    with db_pool.connect() as connection:
        print("Conexão com o banco de dados estabelecida com sucesso!")
except Exception as e:
    print(f"Falha ao conectar com o banco de dados: {e}")