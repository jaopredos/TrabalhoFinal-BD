from app import app
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql import text

from .database import db_pool


@app.route("/mainfunc")
def mainfunc():
    return render_template('funcionario/mainfunc.html')

@app.route("/perfil")
@login_required # Garante que apenas usuários logados podem acessar esta página
def perfil():
    """
    Busca os dados do usuário atualmente logado no banco de dados
    e renderiza a página de perfil com os campos preenchidos.
    """
    user_data = None
    try:
        # Usa o 'current_user.id' (que é o email) para buscar o usuário no banco
        query = text("SELECT * FROM exemplo WHERE email = :email")
        
        with db_pool.connect() as conn:
            # .fetchone() pega a primeira (e única) linha que corresponde à busca
            user_data = conn.execute(query, {"email": current_user.id}).fetchone()

    except Exception as e:
        # Em caso de erro de banco, podemos redirecionar ou mostrar uma página de erro
        print(f"Erro ao buscar dados do perfil: {e}")
        # Futuramente, podemos criar uma página de erro mais amigável
        return "Erro ao carregar seus dados. Tente novamente mais tarde.", 500

    # Se, por algum motivo, o usuário da sessão não for encontrado no banco
    if not user_data:
        # Desloga o usuário e o envia para a página de login
        logout_user()
        return redirect(url_for('login'))

    return render_template("funcionario/att.html", user=user_data)