from sqlalchemy.orm import Session
from datetime import date, timedelta
import decimal

from . import models, schemas, security

# --- Olheiro Services ---
def get_olheiro_by_email(db: Session, email: str):
    return db.query(models.Olheiro).filter(models.Olheiro.email == email).first()

def registrar_novo_olheiro_com_plano(db: Session, olheiro_data: schemas.OlheiroRegistro):
    
    # 1. Busca o plano escolhido para garantir que ele existe e pegar os detalhes
    plano_escolhido = db.query(models.Plano).filter(models.Plano.id == olheiro_data.id_plano).first()
    if not plano_escolhido:
        raise ValueError("Plano selecionado não existe.")

    # Inicia a transação
    try:
        # 2. Cria o registro do Olheiro com a senha hasheada
        hashed_password = security.get_password_hash(olheiro_data.senha)
        db_olheiro = models.Olheiro(
            email=olheiro_data.email, 
            nome_login=olheiro_data.nome_login,
            senha_hash=hashed_password
        )
        db.add(db_olheiro)
        db.flush() # 'Flush' envia para o banco e atribui um ID ao db_olheiro, mas não comita a transação ainda.

        # 3. SIMULA O PAGAMENTO e calcula as datas
        hoje = date.today()
        nova_data_vencimento = hoje + timedelta(days=plano_escolhido.duracao_dias)

        # 4. Cria o registro no histórico de pagamentos para manter o log
        novo_pagamento = models.HistoricoPagamentos(
            id_olheiro=db_olheiro.id, # Usa o ID do olheiro que acabamos de criar
            id_plano=plano_escolhido.id,
            valor_pago=plano_escolhido.valor, # Pega o valor do plano
            id_transacao_gateway=f"sim_{db_olheiro.id}_{hoje.strftime('%Y%m%d')}", # ID de transação simulado
            periodo_coberto_de=hoje,
            periodo_coberto_ate=nova_data_vencimento
        )
        db.add(novo_pagamento)

        # 5. ATUALIZA o olheiro recém-criado com os dados da assinatura
        db_olheiro.id_plano = plano_escolhido.id
        db_olheiro.status_assinatura = models.StatusAssinaturaEnum.ativa
        db_olheiro.data_inicio_assinatura = hoje
        db_olheiro.data_vencimento_assinatura = nova_data_vencimento
        
        # 6. Comita a transação. Se qualquer passo falhar, tudo é desfeito.
        db.commit()
        db.refresh(db_olheiro)
        
        return db_olheiro

    except Exception as e:
        db.rollback() # Desfaz tudo se der erro
        raise e