from .bigquery import client
import pandas as pd
from typing import List, Any, Tuple

def primeiras_n_linhas_tabelao(n=50):
    query = f"""
    SELECT *
    FROM `db-2025-joao-pedro-de-castro.trabalho_nba.nba_nativa`
    LIMIT {n}
"""
    
    query_job = client.query(query)  
    results = query_job.result()  
    return results.to_dataframe()

def get_tabelao():
    query = """
    SELECT *
    FROM `db-2025-joao-pedro-de-castro.trabalho_nba.nba_nativa`
"""
    query_job = client.query(query)
    results = query_job.result()
    return results.to_dataframe()

def atualizar_tabelao(column_name, new_value, condition):
    query = f"""
    UPDATE `db-2025-joao-pedro-de-castro.trabalho_nba.nba_nativa`
    SET {column_name} = {new_value}
    WHERE {condition}
"""
    query_job = client.query(query)  
    results = query_job.result() 
    if results:
        return "Tabela atualizada com sucesso!"
    return "Nenhuma linha atualizada."

def deletar_tabelao(id_linha):
    query = f"""
    DELETE FROM `db-2025-joao-pedro-de-castro.trabalho_nba.nba_nativa`
    WHERE int64_field_0 = {id_linha}
"""
    query_job = client.query(query)
    results = query_job.result()
    if results:
        return "Linha deletada com sucesso!"
    return "Nenhuma linha deletada."


def inserir_no_tabelao(data: List[List[Any]], table_id: str = "db-2025-joao-pedro-de-castro.trabalho_nba.nba_nativa"):
    try:
        table = client.get_table(table_id) # API call para obter o esquema da tabela

        # 2. Inserir as linhas. A biblioteca usará o 'table.schema' automaticamente.
        # Converter para lista de tuplas, pois client.insert_rows() prefere.
        data_as_tuples: List[Tuple[Any, ...]] = [tuple(row) for row in data]

        errors = client.insert_rows(table, data_as_tuples) # Passa a referência da tabela (que contém o esquema)

        if errors:
            print(f"Encontrou erros ao inserir linhas: {errors}")
            # Detalhes dos erros retornados do BigQuery
            for error in errors:
                print(f"Erro na linha: {error['index']}, Mensagem: {error['errors']}")
            raise Exception(f"Erro ao inserir dados no BigQuery: {errors}")
        else:
            return f"Dados inseridos com sucesso na tabela {table_id}."

    except Exception as e:
        print(f"Ocorreu um erro na função inserir_no_tabelao: {e}")
        raise # Re-lança a exceção para ser capturada pelo FastAPI

def consultar_bigquery(
    colunas: list[str] = None,
    tabelas: list[str] = None,
    condicoes_join: list[str] = None,
    filtros: list[str] = None,
    limite: int = 50) -> pd.DataFrame:
    
    if not tabelas:
        raise ValueError("Pelo menos uma tabela deve ser fornecida para a consulta.")

    #Formata as colunas para a consulta
    colunas_str = ", ".join(colunas) if colunas else "*"

    primeira_tabela_info = tabelas[0].split() # Ex: ["db-...", "ft"]
    nome_tabela_base = primeira_tabela_info[0]
    alias_base = primeira_tabela_info[1] if len(primeira_tabela_info) > 1 else ""

    #Contrução da cláusula FROM e JOIN
    from_clause = f"`{nome_tabela_base}`"
    if alias_base: # Se houver alias, adiciona-o
        from_clause += f" {alias_base}"

    if len(tabelas) > 1 and not condicoes_join:
        raise ValueError("Para múltiplas tabelas, as condições de JOIN devem ser fornecidas.")
    
    for i in range(1, len(tabelas)):
        if condicoes_join and len(condicoes_join) >= i:
            tabela_join_info = tabelas[i].split() # Ex: ["db-...", "dj"]
            nome_tabela_join = tabela_join_info[0]
            alias_join = tabela_join_info[1] if len(tabela_join_info) > 1 else ""

            # Use JOIN ou LEFT JOIN conforme a sua necessidade (sua query original usa JOIN = INNER JOIN)
            join_type = "JOIN" # Pode ser parametrizado se precisar de outros tipos de join

            # Adiciona crases ao nome completo da tabela de JOIN
            from_clause += f" {join_type} `{nome_tabela_join}`"
            if alias_join: # Se houver alias, adiciona-o
                from_clause += f" {alias_join}"
            from_clause += f" ON {condicoes_join[i-1]}"
        else:
            raise ValueError(f"Condição de JOIN faltando para a tabela {tabelas[i]}.")

        
    #Construção da cláusula WHERE
    where_clause = ""
    if filtros:
        where_clause = " WHERE " + " AND ".join(filtros)

    query = f"""
    SELECT {colunas_str}
    FROM {from_clause}
    {where_clause}
    LIMIT {limite}
    """
    print(f"Executing query:\n{query}") # Para depuração

    try:
        query_job = client.query(query)
        results = query_job.result()
        return results.to_dataframe()
    except Exception as e:
        # Retorna o erro específico do BigQuery para facilitar a depuração
        raise RuntimeError(f"Erro ao executar a consulta no BigQuery: {e}")