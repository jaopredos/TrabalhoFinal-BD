from app import app
from flask import request, render_template, jsonify, make_response, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from sqlalchemy.sql import text

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
            query = text("SELECT email FROM exemplo WHERE email = :email")
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

        query = text("SELECT email FROM exemplo WHERE email = :email AND senha = :password")
        
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