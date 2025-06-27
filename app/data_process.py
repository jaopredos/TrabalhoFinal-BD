from consultas import get_tabelao
import pandas as pd
from sklearn.preprocessing import StandardScaler

df = get_tabelao()

columns_to_drop = ['int64_field_0','team_abbreviation', 'college', 'country', 'draft_year', 'draft_round', 'draft_number', 'season']
df_processed = df.drop(columns=columns_to_drop)

numerical_features = [
    'age', 'player_height', 'player_weight', 'gp', 'pts', 'reb', 'ast',
    'net_rating', 'oreb_pct', 'dreb_pct', 'usg_pct', 'ts_pct', 'ast_pct'
]


X = df_processed[numerical_features]

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

df_scaled = pd.DataFrame(X_scaled, columns=numerical_features, index=df_processed.index)
df_scaled['player_name'] = df_processed['player_name'] # Manter o nome do jogador para referência