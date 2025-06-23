-- Cria a tabela que vai receber os dados do CSV.
CREATE TABLE usuarios (
    id INT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL, -- ATENÇÃO: Armazenar senhas em texto plano não é seguro. Use hashes em um ambiente real.
    telefone VARCHAR(20),
    tipo_pagamento VARCHAR(50),
    status_pagamento VARCHAR(50),
    jogador VARCHAR(100),
    time VARCHAR(100),
    tipo_plano VARCHAR(50)
);