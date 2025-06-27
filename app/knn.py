import pandas as pd
from sklearn.neighbors import NearestNeighbors
from .data_process import df_processed, numerical_features, scaler, X_scaled


k_recommendations = 3
nn_model = NearestNeighbors(n_neighbors=k_recommendations + 5, metric='euclidean', n_jobs=-1)
nn_model.fit(X_scaled)

def recommend_similar_players(new_player_data, num_recommendations=3):

    # Criar um DataFrame a partir dos dados do novo jogador para garantir a ordem das colunas
    new_player_df = pd.DataFrame([new_player_data])
    
    # Verificar se todas as features necessárias estão presentes
    if not all(feature in new_player_df.columns for feature in numerical_features):
        missing_features = [f for f in numerical_features if f not in new_player_df.columns]
        print(f"Erro: Dados do novo jogador estão faltando as seguintes características: {missing_features}")
        return []

    # Reordenar as colunas do novo jogador para corresponder às features de treinamento
    new_player_features_raw = new_player_df[numerical_features]

    # Normalizar os dados do novo jogador usando o MESMO scaler treinado
    new_player_features_scaled = scaler.transform(new_player_features_raw)

    # Encontrar os vizinhos mais próximos
    # Pegamos mais do que o necessário para poder filtrar o próprio jogador se ele estiver no dataset
    distances, indices = nn_model.kneighbors(new_player_features_scaled)

    similar_players_info = []
    seen_players = set() # Para garantir jogadores únicos na recomendação

    # Pegar o nome do novo jogador, se fornecido, para evitar auto-recomendação
    # Ou, se o novo jogador for um jogador existente no dataset, evitamos ele mesmo
    new_player_name = new_player_data.get('player_name', 'Novo Jogador Desconhecido') # Se houver um nome, use-o
    
    # Iterar sobre os vizinhos encontrados e coletar as informações
    for i in range(len(indices.flatten())):
        idx = indices.flatten()[i]
        
        # Obter o nome e a distância do vizinho
        neighbor_name = df_processed.loc[idx, 'player_name']
        distance = distances.flatten()[i]

        # Verificar se o vizinho não é o próprio jogador e se ainda não foi adicionado
        # A condição `distance > 0` é uma forma de tentar filtrar o próprio jogador se ele for um ponto no dataset
        # Mas o mais robusto é filtrar pelo nome.
        if neighbor_name != new_player_name and neighbor_name not in seen_players:
            similar_players_info.append({'player_name': neighbor_name, 'distance': distance})
            seen_players.add(neighbor_name)
        
        # Parar quando tivermos o número desejado de recomendações
        if len(similar_players_info) >= num_recommendations:
            break
            
    return similar_players_info