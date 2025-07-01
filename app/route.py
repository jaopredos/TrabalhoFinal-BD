from app import app
from flask import request, render_template, jsonify, make_response, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from sqlalchemy.sql import text
from datetime import datetime, timedelta


from .database import db_pool
from .models import User

# --- Início da Configuração do Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        with db_pool.connect() as conn:
            query = text("SELECT email FROM olheiros WHERE email = :email")
            # CORREÇÃO AQUI: Passando parâmetros como um dicionário
            result = conn.execute(query, {"email": user_id}).fetchone()
            if result:
                return User(email=result[0])
    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")
        return None
    return None

# --- Rota de Login Modificada ---
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("\n--- NOVA TENTATIVA DE LOGIN ---")
        
        email = request.form['email']
        password = request.form['password']

        print(f"1. Dados recebidos do formulário -> Email: [{email}], Senha: [{password}]")

        query = text("SELECT email FROM olheiros WHERE email = :email AND senha = :password")
        
        print("2. Código chegou na parte de consultar o SQL. Preparando para executar a query...")
        
        try:
            with db_pool.connect() as conn:
                print("3. Conexão com o banco de dados estabelecida com sucesso.")
                # CORREÇÃO AQUI: Passando parâmetros como um dicionário
                result = conn.execute(query, {"email": email, "password": password}).fetchone()
                print(f"4. Resultado da consulta no banco: {result}")

            if result:
                print("5. Login VÁLIDO (resultado encontrado). Redirecionando para a página principal...")
                user = User(email=result[0])
                login_user(user)
                return redirect(url_for('mainfunc'))
            else:
                print("5. Login INVÁLIDO (nenhum resultado encontrado). Redirecionando de volta para a página de login...")
                flash("Email ou senha inválidos.")
                return redirect(url_for('login'))
                
        except Exception as e:
            print(f"!!! Ocorreu uma EXCEÇÃO ao tentar consultar o banco: {e}")
            flash(f"Erro no servidor: {e}")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/criar_conta", methods=['POST'])
def criar_conta():
    try:
        # 1. Pega os dados do formulário
        nome_login = request.form.get('nome_login')
        email = request.form.get('email')
        senha_plana = request.form.get('senha')
        telefone = request.form.get('telefone')
        id_plano = request.form.get('id_plano', type=int)

        # 2. A linha de criptografia da senha foi removida.

        with db_pool.connect() as conn:
            # Inicia uma transação para garantir a consistência dos dados
            with conn.begin() as trans:
                # 3. Busca a duração do plano selecionado
                plano_query = text("SELECT duracao_dias FROM planos WHERE id = :id_plano")
                plano = conn.execute(plano_query, {"id_plano": id_plano}).fetchone()

                if not plano:
                    flash("Plano selecionado é inválido.", "danger")
                    return redirect(url_for('cadastrar'))

                duracao_dias = plano[0]

                # 4. Calcula as datas de início e vencimento da assinatura
                data_inicio = datetime.now()
                data_vencimento = data_inicio + timedelta(days=duracao_dias)
                
                # 5. Prepara e executa a inserção do novo olheiro
                query_insert = text("""
                    INSERT INTO olheiros 
                    (nome_login, email, senha, telefone, id_plano, data_inicio_assinatura, data_vencimento_assinatura, status_assinatura)
                    VALUES (:nome, :email, :senha, :tel, :id_plano, :inicio, :vencimento, 'periodo_de_teste')
                """)
                
                # O parâmetro 'senha' agora passa a senha plana (sem hash)
                conn.execute(query_insert, {
                    'nome': nome_login,
                    'email': email,
                    'senha': senha_plana,
                    'tel': telefone,
                    'id_plano': id_plano,
                    'inicio': data_inicio,
                    'vencimento': data_vencimento
                })
            # A transação é automaticamente commitada aqui se não houver erros

        flash("Conta criada com sucesso! Por favor, faça o login.", "success")
        return redirect(url_for('login'))

    except Exception as e:
        # Captura erros comuns, como e-mail ou nome de usuário duplicado
        error_message = str(e).lower()
        if 'unique constraint' in error_message or 'duplicate key' in error_message:
            flash("Email ou Nome de Usuário já existem. Por favor, tente outros.", "danger")
        else:
            flash("Ocorreu um erro inesperado ao criar sua conta.", "danger")
            print(f"ERRO AO CRIAR CONTA: {e}")
        
        return redirect(url_for('cadastrar'))

@app.route("/cadastrar") 
def cadast():
    return render_template('cadast.html')

@app.route("/") 
def main():
    return render_template('index.html')

@app.route("/index") 
def index():
    return render_template('index.html')

@app.route("/home") 
@login_required
def home():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template("about.html")