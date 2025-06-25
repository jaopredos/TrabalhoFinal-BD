import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Numeric, Enum
from sqlalchemy.orm import relationship
import datetime

from backend.app.database import Base

class StatusAssinaturaEnum(enum.Enum):
    ativa = "ativa"
    inadimplente = "inadimplente"
    cancelada = "cancelada"
    periodo_de_teste = "periodo_de_teste"

class Plano(Base):
    __tablename__ = "planos"
    id = Column(Integer, primary_key=True, index=True)
    tipo_plano = Column(String, unique=True, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    duracao_dias = Column(Integer, nullable=False) 

class Olheiro(Base):
    __tablename__ = "olheiros" 
    id = Column(Integer, primary_key=True, index=True)
    nome_login = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String) 
    telefone = Column(String, nullable=True)

    id_plano = Column(Integer, ForeignKey("planos.id"), nullable=True)
    data_inicio_assinatura = Column(DateTime, nullable=True)
    data_vencimento_assinatura = Column(Date, nullable=True)
    status_assinatura = Column(Enum(StatusAssinaturaEnum), default=None, nullable=True)
    
    plano = relationship("Plano")
    pagamentos = relationship("HistoricoPagamentos", back_populates="olheiro")

class HistoricoPagamentos(Base):
    __tablename__ = "historico_pagamentos"
    id = Column(Integer, primary_key=True, index=True)
    id_olheiro = Column(Integer, ForeignKey("olheiros.id"), nullable=False)
    id_plano = Column(Integer, ForeignKey("planos.id"), nullable=False)
    data_pagamento = Column(DateTime, default=datetime.datetime.utcnow)
    valor_pago = Column(Numeric(10, 2), nullable=False) # Ex: 99.90
    id_transacao_gateway = Column(String, unique=True, index=True)
    periodo_coberto_de = Column(Date, nullable=False)
    periodo_coberto_ate = Column(Date, nullable=False)
    
    olheiro = relationship("Olheiro")
    plano = relationship("Plano")