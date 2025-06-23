from app import app
from flask import Flask, request, render_template, jsonify
import os
import json
import logging

# Caminho do arquivo JSON
CONTRACTS_FILE = "contratos.json"

# Caminho para o arquivo JSON
ARQUIVO_JSON = "dados_signup.json"

@app.route("/mainfunc")
def mainfunc():
    return render_template('funcionario/mainfunc.html')

# Funcao para carregar os dados existentes no JSON
def carregar_dados():
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as arquivo:
            try:
                return json.load(arquivo)
            except json.JSONDecodeError:
                return []
    return []

# Funcao para salvar os dados no JSON
def salvar_dados(novos_dados):
    dados_existentes = carregar_dados()
    dados_existentes.append(novos_dados)
    
    try:
        with open(ARQUIVO_JSON, 'w', encoding='utf-8') as arquivo:
            json.dump(dados_existentes, arquivo, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar os dados: {e}")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("entrou no metodo")
    if request.method == 'POST':
        print("entrou no metodo")
        user_type = request.form.get('userType')

        if user_type == 'Cliente':
            dados = {
                "tipo": "Cliente",
                "clienteNome": request.form.get('clienteNome'),
                "clienteEmail": request.form.get('clienteEmail'),
                "clienteDepartamentos": request.form.get('clienteDepartamentos'),
                "clienteReceita": request.form.get('clienteReceita'),
                "clienteCnpj": request.form.get('clienteCnpj'),
                "clienteSede": request.form.get('clienteSede'),
                "clienteFuncionarios": request.form.get('clienteFuncionarios'),
                "clientePv": request.form.get('clientePv'),
                "clienteTelefone": request.form.get('clienteTelefone'),
                "clienteIndústria": request.form.get('clienteIndústria'),
                "clienteCapital": request.form.get('clienteCapital'),
                "clienteSenha": request.form.get('clienteSenha')
            }
        elif user_type == 'Funcionario':
            dados = {
                "tipo": "Funcionario",
                "funcionarioNome": request.form.get('funcionarioNome'),
                "funcionarioEmail": request.form.get('funcionarioEmail'),
                "funcionarioSalario": request.form.get('funcionarioSalario'),
                "funcionarioSenha": request.form.get('funcionarioSenha'),
                "funcionarioCpf": request.form.get('funcionarioCpf'),
                "funcionarioCep": request.form.get('funcionarioCep'),
                "funcionarioFormação": request.form.get('funcionarioFormação'),
                "funcionarioTipo": request.form.get('funcionarioTipo'),
                "funcionarioTelefone": request.form.get('funcionarioTelefone'),
                "funcionarioCargo": request.form.get('funcionarioCargo'),
                "funcionarioIdade": request.form.get('funcionarioIdade'),
                "funcionarioGrau": request.form.get('funcionarioGrau')
            }
        else:
            print("Passou direto")
            return "Erro: Tipo de usuário não reconhecido", 400

        # Salva os dados no arquivo JSON
        salvar_dados(dados)

        return render_template('funcionario/signup.html')
    print("Passou direto")

    return render_template('funcionario/signup.html')






@app.route("/attcontract")
def attcontract():
    return render_template('funcionario/attContract.html')

# Função para carregar os contratos do arquivo JSON
def load_contracts():
    if os.path.exists(CONTRACTS_FILE):
        with open(CONTRACTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# Função para salvar os contratos no arquivo JSON
def save_contracts(contracts):
    with open(CONTRACTS_FILE, "w", encoding="utf-8") as file:
        json.dump(contracts, file, indent=4, ensure_ascii=False)

@app.route("/get_contract/<cliente>")
def get_contract(cliente):
    contracts = load_contracts()
    if cliente in contracts:
        return jsonify(contracts[cliente])
    return jsonify({"error": "Cliente não encontrado"}), 404

@app.route("/update_contract/<cliente>", methods=["POST"])
def update_contract(cliente):
    contracts = load_contracts()
    if cliente in contracts:
        data = request.json
        # Atualizar somente os campos existentes, evitando duplicação
        for key in contracts[cliente]:
            if key in data:
                contracts[cliente][key] = data[key]
        save_contracts(contracts)
        return jsonify({"message": "Contrato atualizado com sucesso!"})
    return jsonify({"error": "Cliente não encontrado"}), 404



 



@app.route("/att", methods=['GET'])
def att():
    return render_template("funcionario/att.html")


#identifica o tipo(funcionário ou cliente)
@app.route('/get_identifiers', methods=['GET'])
def get_identifiers():
    user_type = request.args.get('type')

    if not user_type:
        return jsonify({"error": "Tipo de usuário não fornecido"}), 400

    try:
        with open("dados_signup.json", "r") as arquivo:
            dados = json.load(arquivo)

        identifiers = []
        for usuario in dados:
            if user_type == "Cliente":
                if usuario.get("clienteCnpj"):
                    identifiers.append(usuario.get("clienteCnpj"))
            elif user_type == "Funcionario":
                if usuario.get("funcionarioCpf"):
                    identifiers.append(usuario.get("funcionarioCpf"))
        
        return jsonify(identifiers)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#seleciona o cpf/cnpj
@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    user_type = request.args.get('type')
    identifier = request.args.get('id')
    print('1 identfier =', identifier)
    print(user_type)

    if not user_type or not identifier:
        return jsonify({"error": "Parâmetros insuficientes"}), 400

    try:
        with open("dados_signup.json", "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        for usuario in dados:
            print(usuario.get("funcionarioCpf"))
            print('')
            print('comparação')
            print(type(identifier))
            print(type(usuario.get("funcionarioCpf")))
            print('')
            print(usuario)
            if (user_type == "Cliente" and usuario.get("clienteCnpj") == identifier) or \
                (user_type == "Funcionario" and usuario.get("funcionarioCpf") == identifier):
                print('identifier =', identifier)
                print('usertype= ', user_type)
                return jsonify(usuario), 200

        return jsonify({"error": "Usuário não encontrado"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/update_user_data', methods=['POST'])
def update_user_data():
    try:
        # Recebe os dados JSON enviados do frontend
        data = request.get_json()
        user_type = request.args.get('type')
        identifier = request.args.get('id')

        print(f"Tipo de usuário: {user_type}")
        print(f"Identificador: {identifier}")
        print(data)

        # Verifica se os parâmetros necessários foram fornecidos
        if not user_type or not identifier:
            return jsonify({"error": "Tipo de usuário ou identificador não fornecido"}), 400

        # Lê o arquivo JSON para encontrar os dados do cliente/funcionário
        with open("dados_signup.json", "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        # Encontra o cliente/funcionário pelo identificador
        updated = False
        for usuario in dados:
            if (user_type == "Cliente" and usuario.get("clienteCnpj") == identifier) or \
               (user_type == "Funcionario" and usuario.get("funcionarioCpf") == identifier):
                # Atualiza somente os campos enviados (preserva os existentes)
                for key, value in data.items():
                    usuario[key] = value
                updated = True
                break

        if not updated:
            return jsonify({"error": f"{user_type} com identificador '{identifier}' não encontrado"}), 404

        # Escreve os dados atualizados de volta no arquivo JSON
        with open("dados_signup.json", "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)

        return jsonify({"message": f"{user_type} atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
