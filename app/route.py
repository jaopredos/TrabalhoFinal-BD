from app import app
from flask import request, render_template, jsonify, make_response, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import json
login_manager = LoginManager()
login_manager.init_app(app)

#Banco de dados
# Caminho para o arquivo JSON
json_path = "dados_signup.json"

# Lista para armazenar usuários importados
users = []
# Carregando dados do JSON
with open(json_path, 'r') as f:
    data = json.load(f)
    for user in data:
        users.append(user)

#classe de usuário
class User(UserMixin):
    def __init__(self, email, password):
        self.id = email
        self.password = password

#carregando usuários
@login_manager.user_loader
def load_user(email):
    for user in users:
        if user['tipo'] == 'Cliente'and user['clienteEmail'] == (email):
            return User(user['clienteEmail'], user['clienteSenha'])
        elif user['tipo'] == "Funcionario" and user['funcionarioEmail'] == (email):
            return User(user['funcionarioEmail'], user['funcionarioSenha'])
    return None

@app.route("/") 
def main():
    return render_template('index.html') # Está correto

@app.route("/index") 
def index():
    return render_template('index.html') # Está correto

@app.route("/home") 
def home():
    return render_template('index.html') # Está correto

@app.route("/about")
def about():
    return render_template("about.html")

# @app.route("/login")
# def login():
#     return render_template("login.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email, password)
        for user in users:
            if user['tipo'] == "Cliente":
                if user['clienteEmail'] == email and user['clienteSenha'] == password:
                    session['user_email'] = email
                    login_user(User(user['clienteEmail'], user['clienteSenha']))
                    return redirect('/maincli')
            elif user['tipo'] == "Funcionario":
                if user['funcionarioEmail'] == email and user['funcionarioSenha'] == password:
                    session['user_email'] = email
                    login_user(User(user['funcionarioEmail'], user['funcionarioSenha']))
                    return redirect('/mainfunc')
        return "Credenciais inválidas!"
    return render_template('login.html')

