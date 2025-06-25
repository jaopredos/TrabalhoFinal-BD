from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
import decimal

from backend.app.models import StatusAssinaturaEnum

# --- Plano Schemas ---
class PlanoBase(BaseModel):
    tipo_plano: str
    valor: decimal.Decimal
    duracao_dias: int

class Plano(PlanoBase):
    id: int
    class Config:
        orm_mode = True

# --- Olheiro Schemas ---
class OlheiroRegistro(BaseModel):
    email: EmailStr
    nome_login: str
    senha: str
    id_plano: int # O usuário informa o plano que quer contratar

class Olheiro(BaseModel):
    id: int
    email: EmailStr
    nome_login: str
    status_assinatura: Optional[StatusAssinaturaEnum]
    data_vencimento_assinatura: Optional[date]
    class Config:
        orm_mode = True

# --- Token Schema ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    subscription_status: Optional[str] = None


# # --- Pagamento Schema ---
# class PagamentoWebhook(BaseModel):
#     id_transacao: str
#     id_olheiro: int
#     id_plano: int
#     valor_pago: float