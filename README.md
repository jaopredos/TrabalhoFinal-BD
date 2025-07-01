# Trabalho Final de Banco de Dados
![Banco de Dados](image.png)

## Plataforma de Análise de Dados de Jogadores da NBA
por João Pedro de Castro, Bruno Moreira, Cleiver Batista e Bianca Visco

### Introdução
- A nossa motivação para o desenvolvimento disso foi por conta do trabalho final da matéria de Banco de Dados, ministrada pelo professor Sávio Salvarino, no curso de Inteligência Artificial da UFG.
- Precisávamos utilizar dois tipos de bancos de dados distintos e, além disso, precisávamos realizar algumas análises dos nossos dados em plataformas de BI. 
- Para usar dois bancos de dados distintos, usaremos o Banco de Dados Relacional, mais especificamente o Postgres, para cuidar da parte de login e cadastro da nossa plataforma e o Data Warehouse, mais especificamente o BigQuery, para armazenar os nossos dados dos jogadores.
- Depois que tivemos a ideia do que fazermos, fomos atrás dos [dados](https://www.kaggle.com/datasets/justinas/nba-players-data).
- 

### Instruções para rodar o código:

* Criar arquivo .env com as credenciais para o Cloud Postgres SQL e um arquivo ".json" com as credenciais da API do Big Query
* Dar um pip install -r requirements.txt
* Iniciar ele pelo arquivo mainFlask.py