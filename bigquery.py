import os
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()


google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if google_credentials_path:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials_path
    print(f"Credenciais carregadas de: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")
else:
    print("Variável GOOGLE_APPLICATION_CREDENTIALS não encontrada no .env")

client = bigquery.Client()