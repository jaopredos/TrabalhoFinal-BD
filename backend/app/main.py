from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import date

from . import models, schemas, services, security
from .database import engine, get_db

# Cria as tabelas no banco de dados (se não existirem)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/registrar", response_model=schemas.Olheiro, status_code=status.HTTP_201_CREATED)
def registrar_olheiro_e_ativar_plano(olheiro_data: schemas.OlheiroRegistro, db: Session = Depends(get_db)):
    # Verifica se o email já existe
    db_olheiro = services.get_olheiro_by_email(db, email=olheiro_data.email)
    if db_olheiro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
    
    try:
        # Chama a nova função de serviço que faz todo o trabalho
        return services.registrar_novo_olheiro_com_plano(db=db, olheiro_data=olheiro_data)
    except ValueError as e:
        # Erro caso o plano não exista
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        # Outros erros
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocorreu um erro ao criar a conta.")

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Autentica o usuário (verifica email e senha)
    user = services.get_olheiro_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. VERIFICA O STATUS DA ASSINATURA ANTES DE GERAR O TOKEN
    is_active = False
    if user.status_assinatura == models.StatusAssinaturaEnum.ativa and user.data_vencimento_assinatura:
        if user.data_vencimento_assinatura >= date.today():
            is_active = True

    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # Código "Proibido"
            detail="Sua assinatura não está ativa. Por favor, renove para continuar."
        )

    # 3. Se tudo estiver OK, gera e retorna o token
    data_for_token = {"sub": user.email} # Simplificado por enquanto
    access_token = security.create_access_token(data=data_for_token)
    
    return {"access_token": access_token, "token_type": "bearer"}