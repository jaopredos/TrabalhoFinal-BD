from flask import Flask, request, jsonify
import consultas as queries
from knn import recommend_similar_players

app = Flask(__name__)

@app.route('/queryBQ', methods=['POST'])
def consulta_bigquery_personalizada_flask():
    """
    Endpoint para realizar consultas flexíveis no BigQuery, permitindo seleção de colunas,
    junção de tabelas e aplicação de filtros.
    """
    try:
        request_data = request.get_json()

        if not request_data:
            return jsonify({"detail": "Corpo da requisição JSON inválido ou vazio."}), 400
        
        colunas = request_data.get('colunas')
        tabelas = request_data.get('tabelas')
        condicoes_join = request_data.get('condicoes_join')
        filtros = request_data.get('filtros')
        limite = request_data.get('limite', 50) # Define 50 como padrão, como no seu modelo

        # Validação manual para 'tabelas', que é obrigatória e deve ter pelo menos um item
        if not tabelas or not isinstance(tabelas, list) or len(tabelas) == 0:
            return jsonify({"detail": "'tabelas' é um campo obrigatório e deve ser uma lista não vazia de strings."}), 400
        
        # Validação para 'limite'
        if not isinstance(limite, int) or limite < 1:
            return jsonify({"detail": "'limite' deve ser um número inteiro maior ou igual a 1."}), 400
        
        df = queries.consultar_bigquery( # Ou queries.consultar_bigquery(...)
            colunas=colunas,
            tabelas=tabelas,
            condicoes_join=condicoes_join,
            filtros=filtros,
            limite=limite
        )
        return jsonify(df.to_dict(orient='records')), 200

    except ValueError as ve:
        # Retorna 400 Bad Request para erros de validação da sua função de consulta
        return jsonify({"detail": str(ve)}), 400
    except RuntimeError as re:
        # Retorna 500 Internal Server Error para erros específicos de execução da sua consulta
        return jsonify({"detail": str(re)}), 500
    except Exception as e:
        # Captura qualquer outro erro inesperado
        return jsonify({"detail": f"Ocorreu um erro inesperado: {e}"}), 500


@app.route('/getNativa', methods=['GET'])
def get_n_linhas_nativa_flask():
    try:
        n = request.args.get('n', default=50, type=int)
        df = queries.primeiras_n_linhas_tabelao(n)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"detail": f"Erro ao consultar dados: {e}"}), 500
    
@app.route('/updateBQ', methods=['POST'])
def update_bigquery_flask():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"detail": "Corpo da requisição JSON inválido ou vazio."}), 400

        column_name = data.get('column_name')
        new_value = data.get('new_value')
        condition = data.get('condition')

        if not all([column_name, new_value, condition]):
            return jsonify({"detail": "Campos 'column_name', 'new_value' e 'condition' são obrigatórios."}), 400
        message = queries.atualizar_tabelao(column_name, new_value, condition) # Ou queries.atualizar_tabelao(...)

        return jsonify({"message": message}), 200
    
    except Exception as e:
        # Retorna um JSON com o erro e o status HTTP 500
        return jsonify({"detail": f"Erro ao atualizar os dados: {e}"}), 500

@app.route('/deleteBQ', methods=['POST'])
def delete_bigquery_flask():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"detail": "Corpo da requisição JSON inválido ou vazio."}), 400

        id_linha = data.get('id_linha')

        # Validação básica para garantir que o id_linha foi fornecido e é um inteiro
        if id_linha is None: # Verifica se a chave existe e não é None
            return jsonify({"detail": "O campo 'id_linha' é obrigatório."}), 400
        
        if not isinstance(id_linha, int):
            return jsonify({"detail": "O campo 'id_linha' deve ser um número inteiro."}), 400
        
        message = queries.deletar_tabelao(id_linha) # Ou queries.deletar_tabelao(id_linha)

        return jsonify({"message": message}), 200

    except Exception as e:
        # Retorna um JSON com o erro e o status HTTP 500
        return jsonify({"detail": f"Erro ao deletar dados: {e}"}), 500

@app.route('/insertBQ', methods=['POST'])
def insert_bigquery_flask():
    try:
        data_to_insert = request.get_json()

        if not data_to_insert:
            return jsonify({"detail": "Corpo da requisição JSON inválido ou vazio."}), 400

        # Validação básica para garantir que é uma lista de listas
        if not isinstance(data_to_insert, list) or not all(isinstance(item, list) for item in data_to_insert):
            return jsonify({"detail": "Os dados para inserção devem ser uma lista de listas (e.g., [[val1, val2], [val3, val4]])."})

        message = queries.inserir_no_tabelao(data_to_insert) # Ou queries.inserir_no_tabelao(data_to_insert)

        return jsonify({"message": message}), 200

    except Exception as e:
        # Retorna um JSON com o erro e o status HTTP 500
        return jsonify({"detail": f"Erro ao inserir dados: {e}"}), 500
    
@app.route('/similarPlayers', methods=['POST'])
def similar_players_flask():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"detail": "Corpo da requisição JSON inválido ou vazio."}), 400

        # Obtém os dados do novo jogador e o número de recomendações
        new_player_data = data.get('new_player_data')
        num_recommendations = data.get('num_recommendations', 3) # Define 3 como padrão se não for fornecido

        # Validação básica
        if not new_player_data or not isinstance(new_player_data, dict):
            return jsonify({"detail": "'new_player_data' é obrigatório e deve ser um dicionário."}), 400
        
        if not isinstance(num_recommendations, int) or num_recommendations <= 0:
            return jsonify({"detail": "'num_recommendations' deve ser um inteiro positivo."}), 400
        
        recommended_players = recommend_similar_players(new_player_data, num_recommendations)

        if not recommended_players:
            # Em Flask, você retorna um JSON e o status, não eleva HTTPException
            return jsonify({"detail": "Nenhum jogador similar encontrado."}), 404
            
        return jsonify(recommended_players), 200 # Retorna a lista de dicionários como JSON

    except Exception as e:
        # Captura qualquer outro erro e retorna 500 Internal Server Error
        return jsonify({"detail": f"Erro ao recomendar jogadores: {e}"}), 500
    




if __name__ == '__main__':
    app.run(debug=True)