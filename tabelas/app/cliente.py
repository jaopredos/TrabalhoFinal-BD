from app import app
from flask import request, render_template, jsonify, make_response

@app.route("/contract")
def contract():
    return render_template('cliente/contract.html')

@app.route("/predict") 
def predict():
    return render_template('cliente/predict.html')


@app.route("/maincli")
def maincli():
    return render_template('cliente/maincli.html')

@app.route("/suport", methods=["GET", "POST"])
def suport():
    if request.method == "POST":
        # Obtenha os valores do formulário
        assunto = request.form.get("assunto")
        descricao = request.form.get("descricao")

        # Crie uma variável com os dados
        suporte_data = {
            "assunto": assunto,
            "descricao": descricao
        }

        # Print os dados no console
        print(suporte_data)

        # Retorne uma resposta (opcional, você pode redirecionar ou exibir uma mensagem)
        return render_template('cliente/suport.html', mensagem="Suporte enviado com sucesso!")

    # Para requisições GET, apenas renderize o HTML
    return render_template('cliente/suport.html')