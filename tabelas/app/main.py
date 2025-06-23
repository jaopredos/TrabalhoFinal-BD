from flask import Flask, request, jsonify
from flask import render_template
from app import app
from flask_cors import CORS
from pathlib import Path
import logging
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as m
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score



def supermercadoKaggle(pasta):
    df = pd.read_csv(pasta, encoding='latin1')

    # Verificando se a coluna 'Date' está presente
    if 'Date' not in df.columns:
        raise ValueError("A coluna 'Date' não está presente no arquivo CSV")

    # Convertendo a coluna 'Date' para datetime
    try:
        df['Date'] = pd.to_datetime(df['Date'])
    except Exception as e:
        raise ValueError(f"Erro ao converter a coluna 'Date' para datetime: {e}")

    # Armazenando a última data antes de remover a coluna 'Date'
    last_date = df['Date'].max()

    # Extraindo características da data
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week
    df['DayOfWeek'] = df['Date'].dt.dayofweek

    # Removendo colunas desnecessárias
    df.drop(['Invoice ID', 'gross margin percentage', 'Date', 'Time', 'cogs', 'gross income'], axis=1, inplace=True)

    target = "Quantity"
    results = {}

    # Iterando sobre cada categoria de 'Product line'
    for product_line in df['Product line'].unique():
        df_product = df[df['Product line'] == product_line].copy()
        sameData = df_product.groupby(['Year','Month','WeekOfYear','DayOfWeek']).size()
        sameDataMean = sameData.mean()


        X = df_product.drop(target, axis=1)
        y = df_product[target]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        #Transformação de dados
        num_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])

        nom_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder())
        ])
        preprocessor = ColumnTransformer(transformers=[
            ("num_features", num_transformer, ["Unit price", "Tax 5%", "Rating", "Total", "Year", "Month", "WeekOfYear", "DayOfWeek"]),
            ("nom_features", nom_transformer, ["Branch", "City", "Customer type", "Payment", "Gender"])
        ])

        model = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", GradientBoostingRegressor(max_depth=6, random_state=42))
        ])

        #Fitando o modelo
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)


        # Adicionando variabilidade nos dados futuros
        def add_variability(data, variability_factor=0.1):
            return data * (1 + np.random.uniform(-variability_factor, variability_factor, data.shape))

        # Para prever a próxima semana
        future_dates_week = [last_date + pd.DateOffset(days=i) for i in range(1, 8)]
        future_df_week = pd.DataFrame({
            'Year': [date.year for date in future_dates_week],
            'Month': [date.month for date in future_dates_week],
            'WeekOfYear': [date.isocalendar().week for date in future_dates_week],
            'DayOfWeek': [date.dayofweek for date in future_dates_week],
            'Unit price': add_variability(np.array([X_test['Unit price'].mean()]*7)),
            'Tax 5%': add_variability(np.array([X_test['Tax 5%'].mean()]*7)),
            'Rating': add_variability(np.array([X_test['Rating'].mean()]*7)),
            'Total': add_variability(np.array([X_test['Total'].mean()]*7)),
            'Branch': [X_test['Branch'].mode()[0]]*7,
            'City': [X_test['City'].mode()[0]]*7,
            'Customer type': [X_test['Customer type'].mode()[0]]*7,
            'Payment': [X_test['Payment'].mode()[0]]*7,
            'Gender': [X_test['Gender'].mode()[0]]*7,
            'Product line': [product_line]*7  # Mantendo a linha do produto constante
        })

        #Fazendo as previsões para os próximos 7 dias
        future_pred_week = model.predict(future_df_week)
        future_pred_week = future_pred_week * sameDataMean
        future_pred_week_sum = round(sum(future_pred_week), 0) 


        results[product_line] = {
            "future_pred_week": future_pred_week_sum,
            "category": product_line,
        }

    return results


def codigo10MilLinhas(pasta):
    df = pd.read_csv(pasta, encoding='latin1')
    
    # Verificando se a coluna 'Data' está presente
    if 'Data' not in df.columns:
        raise ValueError("A coluna 'Date' não está presente no arquivo CSV")

    # Convertendo a coluna 'Data' para datetime
    try:
        df['Data'] = pd.to_datetime(df['Data'])
    except Exception as e:
        raise ValueError(f"Erro ao converter a coluna 'Date' para datetime: {e}")

    # Armazenando a última data antes de remover a coluna 'Data'
    last_date = df['Data'].max()

    # Extraindo características da data
    df['Year'] = df['Data'].dt.year
    df['Month'] = df['Data'].dt.month
    df['WeekOfYear'] = df['Data'].dt.isocalendar().week
    df['DayOfWeek'] = df['Data'].dt.dayofweek
    
    df = df.loc[(df['N_PRODUTO'] == 1)]
    df.drop(['NFISCAL', 'VENDEDOR', 'SUPERVISOR', 'Data', 'SCORE', 'N_LINHA', 'CLASSIFICACAO', 'CANAL_VENDA', 'N_CATEGORIA', 'N_PRODUTO', 'V_CUSTO_VENDA', 'V_MARGEM_T'], axis=1, inplace=True)

    #Codificando colunas categóricas
    label_encoders = {}
    for column in ['CLIENTE', 'Cidade']:
        le = LabelEncoder()
        df[column] = le.fit_transform(df[column])
        label_encoders[column] = le
    target = "QTD_ITEM"
    X = df.drop(target, axis=1)
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)

    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    nom_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder())
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num_features", num_transformer, ['V_PERC_MARGEM_T', 'V_CUSTO_TOTAL', 'V_MARGEM', 'V_CMV', 'V_VENDA', 'CLIENTE']),
        ("nom_features", nom_transformer, ['Estado'])
    ])

    model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", GradientBoostingRegressor(max_depth=6, random_state=100))
    ])



    #Fitando o modelo
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    # Função para adicionar variabilidade aos dados futuros
    def add_variability(data, variability_factor=0.1):
        return data * (1 + np.random.uniform(-variability_factor, variability_factor, data.shape))
    
    # Previsão para a próxima semana
    future_dates_week = [last_date + pd.DateOffset(days=i) for i in range(1, 8)]
    future_df_week = pd.DataFrame({
        'Year': [date.year for date in future_dates_week],
        'Month': [date.month for date in future_dates_week],
        'WeekOfYear': [date.isocalendar().week for date in future_dates_week],
        'DayOfWeek': [date.dayofweek for date in future_dates_week],
        'V_PERC_MARGEM_T': add_variability(np.array([X_test['V_PERC_MARGEM_T'].mean()]*7)),
        'V_CUSTO_TOTAL': add_variability(np.array([X_test['V_CUSTO_TOTAL'].mean()]*7)),
        'V_MARGEM': add_variability(np.array([X_test['V_MARGEM'].mean()]*7)),
        'V_CMV': add_variability(np.array([X_test['V_CMV'].mean()]*7)),
        'V_VENDA': add_variability(np.array([X_test['V_VENDA'].mean()]*7)),
        'CLIENTE': [X_test['CLIENTE'].mode()[0]]*7,
        'Estado': [X_test['Estado'].mode()[0]]*7
    })
    
    #Fazendo as previsões para os próximos 7 dias
    future_pred_week = model.predict(future_df_week)
    future_pred_week = [round(pred, 0) for pred in future_pred_week]

    results = {
        "future_pred_week": future_pred_week,
        "future_dates_week": [date.strftime("%Y-%m-%d") for date in future_dates_week]
    }

    return results

#Simulação de Monte Carlo
def monteCarlo(pasta, save_dir, filename):
    # Imports para formatação dos gráficos
    plt.style.use('fivethirtyeight')
    m.rcParams['axes.labelsize'] = 14
    m.rcParams['xtick.labelsize'] = 12
    m.rcParams['ytick.labelsize'] = 12
    m.rcParams['text.color'] = 'white'
    from matplotlib.pylab import rcParams
    rcParams['figure.figsize'] = 20,10

    #formatando valores com duas casas decimais
    pd.options.display.float_format = '{:.2f}'.format

    #Iportar arquivo
    df = pasta
    
    df = df[['Date', 'gross income']] #Selecionando as colunas desejadas
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce') #Transformando a coluna Date em datetime
    df.dropna(subset=['Date'], inplace=True) #Retirar linhas com datas inválidas
    df.set_index('Date', inplace=True) #Indexar as datas
    df.columns = ['Renda_Bruta'] #Renomear a coluna
    df = df.resample('D').sum() #Agrupar por dia
    
    retorno_diario = df['Renda_Bruta'].pct_change().dropna() #Calcular o retorno diário, quanto o valor de fechamento varia de um dia para outro

    df = pd.merge(df, retorno_diario, how = 'inner', on = 'Date') #Juntar as duas tabelas
    df.columns = ['Renda_Bruta', 'Variação_Diaria'] #Renomear as colunas

    #Vamos usar a estatística para calcular o retorno médio e a variação (desvio padrão).
    media_retorno_diario = np.mean(retorno_diario) #Média do fechamento diário da renda_bruta
    desvio_retorno_diario = np.std(retorno_diario) #Desvio padrão do fechamento diário da renda_bruta

    
    # Transformação de log e diferenciação para cálculo do retorno diário
    log_retorno_diario = (np.log(df["Renda_Bruta"]) - np.log(df["Renda_Bruta"]).shift(-1)).dropna()

    # Calculamos média e desvio padrão após a transformação
    log_media_retorno_diario = np.mean(log_retorno_diario)
    log_desvio_retorno_diario = np.std(log_retorno_diario)
    
    # Número de dias a frente
    dias_posteriores = 15

    # Número de simulações
    simulacoes = 15

    # Último valor da ação
    ultimo_preco = 213.67

    # Cria um array vazio com as dimensões
    results = np.empty((simulacoes, dias_posteriores))

    # Loop por cada simulação
    for s in range(simulacoes):

        # Calcula o retorno com dados randômicos seguindo uma distribuição normal
        random_returns = 1 + np.random.normal(loc = log_media_retorno_diario,
                                            scale = log_desvio_retorno_diario,
                                            size = dias_posteriores)

        result = ultimo_preco * (random_returns.cumprod())

        results[s, :] = result
    
    # Definindo o índice da série simulada
    index = pd.date_range("2019-03-30", periods = dias_posteriores, freq = "D")
    resultados = pd.DataFrame(results.T, index = index)
    media_resultados = resultados.apply("mean", axis = 1)

    # Dividindo a área de plotagem em 2 subplots
    fig, ax = plt.subplots(nrows = 2, ncols = 1)

    # Plot
    ax[0].plot(df["Renda_Bruta"][:"2019-04-15"])

    ax[0].plot(resultados)

    ax[0].axhline(213.67, c = "orange")

    ax[0].set_title(f"Monte Carlo {simulacoes} Simulações", size = 14)

    ax[0].legend(["Preço Histórico", "Último Preço = 213.67"])

    ax[1].plot(df["Renda_Bruta"][:"2019-04-15"])

    ax[1].plot(resultados.apply("mean", axis = 1), lw = 2 , c = "white")

    ax[1].plot(media_resultados.apply((lambda x: x * (1+1.96 * log_desvio_retorno_diario))),
            lw = 2, linestyle = "dotted", c = "gray")

    ax[1].plot(media_resultados, lw = 2, c = "orange")

    ax[1].plot(media_resultados.apply((lambda x: x * (1-1.96 * log_desvio_retorno_diario))),
            lw = 2, linestyle = "dotted", c = "gray")

    ax[1].set_title(f"Resultado Médio Monte Carlo Simulações", size = 14, )

    ax[1].legend(["Preço", "Previsão Média", "2x Desvio Padrao"], )
    
    file_path = save_dir / filename
    plt.savefig(file_path, transparent=True)  # Salvar com fundo transparente
    plt.close()
    
    if not file_path.is_file():
        raise RuntimeError(f"Failed to save barh plot to {file_path}")


#Coluna só pra período do mês
def categorizar_dia(dia):
    if dia <= 10:
        return 'início'
    elif dia <= 20:
        return 'meio'
    else:
        return 'fim'


#função: Gráfico de Frequência (Barras Horizontais)
def plot_barh(data, COLUNA, NOME_Y, NOME_X, NOME_TITULO, qntd_divisao_x, borda_preta, escala, save_dir, filename):
    plt.figure(figsize=(6.4*escala, 4.8*escala), dpi=300)
    if borda_preta == 1:
        data.groupby(COLUNA).size().plot(kind='barh', color=sns.palettes.mpl_palette('cool'), edgecolor='black')
    else:
        data.groupby(COLUNA).size().plot(kind='barh', color=sns.palettes.mpl_palette('cool'))
    plt.title(NOME_TITULO, fontsize=20, color="white")
    plt.xlabel(NOME_X, fontsize=20, color="white")
    plt.ylabel(NOME_Y, fontsize=20, color="white")
    step_size_x = max(1, data[COLUNA].value_counts().max() // qntd_divisao_x)
    ticksx = range(0, int(data[COLUNA].value_counts().max()) + 1, step_size_x)
    plt.xticks(ticksx, fontsize=10, rotation=45, color="white")
    plt.yticks(fontsize=15, color="white")
    plt.gca().spines[['top', 'right']].set_visible(False)
    
    
    file_path = save_dir / filename
    plt.savefig(file_path, transparent=True)  # Salvar com fundo transparente
    plt.close()
    
    if not file_path.is_file():
        raise RuntimeError(f"Failed to save barh plot to {file_path}")


def plot_pie(data, COLUNA, NOME_TITULO, escala, save_dir, filename):
    
    #Contar a frequencia de cada superVisor
    contagem = data[COLUNA].value_counts().sort_index()

    # Plotar o gráfico de pizza
    plt.figure(figsize=(6*escala, 6*escala))
    explode = [0.02] * len(contagem)
    wedges, texts, autotexts = plt.pie(contagem, labels=contagem.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('cool'),wedgeprops={'edgecolor': 'black', 'linewidth': 1},explode=explode)
    plt.setp(texts, color='white')
    plt.setp(autotexts, color='black')
    plt.title(NOME_TITULO, color="white")


    
    file_path = save_dir / filename  # Usar Path para manipulação de caminhos
    plt.savefig(file_path, transparent=True)
    plt.close()
    
    if not file_path.is_file():
        raise RuntimeError(f"Failed to save barh plot to {file_path}") 
    
def plot_histogram(data, COLUNA, NOME_Y, NOME_X, NOME_TITULO, range_x, qntd_divisão_y, borda_preta, escala, save_dir, filename):
    # Criar o gráfico
    plt.figure(figsize=(6.4*escala, 4.8*escala), dpi=150)
    n_bins = max(data[COLUNA])
    counts, bins, patches = plt.hist(data[COLUNA].dropna(), bins=n_bins, edgecolor='black' if borda_preta == 1 else None, width=0.9)

    # Aplicar a paleta de cores "cool" às barras
    cmap = plt.cm.cool
    norm = plt.Normalize(vmin=min(counts), vmax=max(counts))

    for count, patch in zip(counts, patches):
        color = cmap(norm(count))
        patch.set_facecolor(color)

    plt.title(NOME_TITULO, fontsize=20, color="white")
    plt.ylabel(NOME_Y, fontsize=15, color="white")
    plt.xlabel(NOME_X, fontsize=15, color="white")

    ticksx = range(int(data[COLUNA].min()), int(data[COLUNA].max()) + 1, range_x)
    step_size_y = max(1, data[COLUNA].value_counts().max() // qntd_divisão_y)
    ticksy = range(0, int(data[COLUNA].value_counts().max()) + 1, step_size_y)

    plt.xticks(ticksx, fontsize=10, rotation=45, color="white")
    plt.yticks(ticksy, fontsize=10, color="white")
    plt.gca().spines[['top', 'right']].set_visible(False)

    file_path = Path(save_dir) / filename  # Usar Path para manipulação de caminhos
    plt.savefig(file_path, transparent=True)
    plt.close()

    if not file_path.is_file():
        raise RuntimeError(f"Failed to save barh plot to {file_path}")
    
def plot_histogram_with_interval(data, COLUNA, NOME_Y, NOME_X, NOME_TITULO, range_x, qntd_divisão_y, borda_preta, zoom_max, escala, save_dir, filename):
    #Capturar intervalo do usuário
    min_x = int(input("Digite o valor mínimo do intervalo do eixo 'X': "))
    max_x = int(input("Digite o valor máximo do intervalo do eixo 'X': "))

    # Filtrar dados no intervalo especificado
    filtered_data = data[(data[COLUNA] >= min_x) & (data[COLUNA] <= max_x)]
    # Verificar se há dados suficientes no intervalo especificado
    if filtered_data.empty:
        print("Não há produtos no intervalo especificado.")
        return
    # Verificar se o eixo x está dentro do zoom_max
    if max_x - min_x > zoom_max:
        print(f"O eixo x está fora do zoom máximo({zoom_max}).")
        return
    #Criar o gráfico
    plt.figure(figsize=(6.4*escala, 4.8*escala), dpi=150)
    if borda_preta == 1:
        plt.hist(filtered_data[COLUNA].dropna(), bins=range(min_x, max_x + 2), edgecolor='black',width=0.9)
    else:
        plt.hist(filtered_data[COLUNA].dropna(), bins=range(min_x, max_x + 2), width=0.9)
    plt.title(NOME_TITULO, fontsize=20, color="white")
    plt.ylabel(NOME_Y, fontsize=15, color="white")
    plt.xlabel(NOME_X, fontsize=15, color="white")
    ticksx = range(min_x, max_x + 1, range_x)
    step_size_y = max(1, filtered_data[COLUNA].value_counts().max() // qntd_divisão_y)
    ticksy = range(0, int(filtered_data[COLUNA].value_counts().max()) + 1, step_size_y)
    plt.xticks(ticksx, fontsize=10, rotation=45, color="white")
    plt.yticks(ticksy, fontsize=10, color="white")
    plt.gca().spines[['top', 'right',]].set_visible(False)
    
    file_path = save_dir / filename  # Usar Path para manipulação de caminhos
    plt.savefig(file_path, transparent=True)
    plt.close()
    
    if not file_path.is_file():
        raise RuntimeError(f"Failed to save barh plot to {file_path}") 

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path() / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True) # Certificar se o diretório de uploads existe

# Configurações do Flask
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16 MB

# Função utilitária para leitura de CSV com diferentes codificações
def read_csv_with_encoding(file_path, encodings=['utf-8', 'latin1', 'iso-8859-1']):
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"Arquivo lido com sucesso usando codificação: {encoding}")
            return df
        except UnicodeDecodeError:
            logger.warning(f"Erro ao ler o arquivo com codificação: {encoding}")
    raise ValueError("Não foi possível ler o arquivo com as codificações fornecidas.")



@app.route('/uploadfile', methods=['POST'])
def upload_file():
    if 'file_upload' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file_upload']

    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Formato de arquivo inválido. Apenas .csv é permitido"}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logger.info(f"Arquivo recebido: {filename}")

        if filename == "supermarket_sales_-_Sheet1.csv":
            isCodigo10MilLinhas = False
            df = read_csv_with_encoding(file_path)
            result = {"message": "Dados processados para supermercado"}
            
            df['Date'] = pd.to_datetime(df['Date'])
            df['Mes'] = df['Date'].dt.month
            df['Ano'] = df['Date'].dt.year
            df['Dia'] = df['Date'].dt.day
            df['Período'] = df['Dia'].apply(categorizar_dia)

            # Coluna Nome dos meses
            meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
            df['Mes_Nome'] = df['Mes'].map(meses)
            
            plot_barh(df, 'Product line', 'Linha dos Produtos', 'Frequência', 'Linha dos produtos mais vendidos', 10, 1, 3.5, UPLOAD_DIR, "barh.png")
            plot_pie(df, 'Branch', 'Frequência da Filial', 1, UPLOAD_DIR, "filial.png")
            plot_pie(df, 'Período', 'Frequência de Perídos do Mês', 1, UPLOAD_DIR, "mes.png")
            plot_barh(df, 'Customer type', 'Tipo do Cliente', 'Frequência de compra', 'Tipo de clientes que mais compram', 20, 1, 2.5, UPLOAD_DIR, "clientes.png")
            plot_pie(df, "Payment", 'Frequência dos meios de pagamentos', 1, UPLOAD_DIR, "pagamento.png")
            plot_barh(df, 'Gender', 'Tipo de Gênero do Cliente', 'Frequência de gênero', 'Tipo de clientes que mais compram', 20, 1, 2.5, UPLOAD_DIR, "genero.png")
            
            monteCarlo(df, UPLOAD_DIR, "monteCarlo.png")
        elif filename == "Cópia de vendas.csv":
            isCodigo10MilLinhas = True
            df = read_csv_with_encoding(file_path)
            result = {"message": "Dados processados para 10 mil linhas"}
            
            df['Date'] = pd.to_datetime(df['Date'])
            df['Mes'] = df['Date'].dt.month
            df['Ano'] = df['Date'].dt.year
            df['Dia'] = df['Date'].dt.day
            df['Período'] = df['Dia'].apply(categorizar_dia)

            # Coluna Nome dos meses
            meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
            df['Mes_Nome'] = df['Mes'].map(meses)
            
            plot_histogram(df, 'N_PRODUTO', 'Frequência', 'Produtos', 'Distribuição dos Produtos', 20, 10, 0, 2, UPLOAD_DIR, "clientes.png")
            plot_histogram(df, 'N_CATEGORIA', 'Frequência', 'Categorias', 'Distribuição das Categorias', 1, 10, 1, 2, UPLOAD_DIR, "barh.png")
            plot_barh(df, 'CANAL_VENDA', 'Canal de Vendas', 'Frequência', 'Canais de Vendas mais utilizados', 10, 1, 2, UPLOAD_DIR, "pagamento.png")
            plot_barh(df, 'SUPERVISOR', 'Supervisor', 'Frequência', 'Supervisor mais eficiente', 10, 1, 2.8, UPLOAD_DIR, "genero.png")
            plot_barh(df, 'Estado', 'Estado', 'Frequência', 'Estado com mais vendas', 50, 0, 3, UPLOAD_DIR, "filial.png")
            plot_barh(df, 'Mes', 'Mês', 'Frequência', 'Mês com mais vendas', 10, 1, 2, UPLOAD_DIR, "mes.png")
        else:
            return jsonify({"error": "Arquivo desconhecido"}), 400

        return render_template('cliente/predict.html', 
                                filename=filename,
                                result=result,
                                isCodigo10MilLinhas=isCodigo10MilLinhas,
                                plot_url='barh.png',
                                plot_url_clientes='clientes.png',
                                plot_url_genero='genero.png',
                                plot_url_filial='filial.png',
                                plot_url_mes='mes.png',
                                plot_url_pagamento='pagamento.png',
                                plot_url_monteCarlo='monteCarlo.png')

    except Exception as e:
        logger.error(f"Erro ao processar o arquivo: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Servir arquivos estáticos do diretório de uploads
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    

#Roda as funções de todos os gráficos
#            plot_barh(df, 'Product line', 'Linha dos Produtos', 'Frequência', 'Linha dos produtos mais vendidos', 10, 1, 3.5, UPLOAD_DIR, "barh.png")
#            plot_pie(df, 'Branch', 'Frequência da Filial', 1, UPLOAD_DIR, "filial.png")
#         plot_pie(df, 'Período', 'Frequência de Perídos do Mês', 1, UPLOAD_DIR, "mes.png")
#          plot_barh(df, 'Customer type', 'Tipo do Cliente', 'Frequência de compra', 'Tipo de clientes que mais compram', 20, 1, 2.5, UPLOAD_DIR, "clientes.png")
#         plot_pie(df, "Payment", 'Frequência dos meios de pagamentos', 1, UPLOAD_DIR, "pagamento.png")
#            plot_barh(df, 'Gender', 'Tipo de Gênero do Cliente', 'Frequência de gênero', 'Tipo de clientes que mais compram', 20, 1, 2.5, UPLOAD_DIR, "genero.png")