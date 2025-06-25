import decimal
from app.database import SessionLocal
from app import models

def seed_plans():
    """
    Popula a tabela de Planos com os dados iniciais.
    Este script é idempotente, ou seja, pode ser executado várias vezes sem criar duplicatas.
    """
    db = SessionLocal()
    
    print("Iniciando o seeding da tabela de Planos...")

    # 1. Define os planos que queremos no nosso sistema
    planos_a_criar = [
        {
            "tipo_plano": "Mensal",
            "valor": decimal.Decimal("29.90"),
            "duracao_dias": 30
        },
        {
            "tipo_plano": "Semestral",
            "valor": decimal.Decimal("149.90"), # Ex: um desconto de ~16%
            "duracao_dias": 180
        },
        {
            "tipo_plano": "Anual",
            "valor": decimal.Decimal("299.90"), # Ex: um desconto de ~17%, paga 10 meses e leva 12
            "duracao_dias": 365
        }
    ]

    try:
        for plano_data in planos_a_criar:
            # 2. Verifica se o plano já existe antes de tentar criar
            plano_existente = db.query(models.Plano).filter(models.Plano.tipo_plano == plano_data["tipo_plano"]).first()
            
            if not plano_existente:
                # 3. Se não existe, cria o novo plano
                novo_plano = models.Plano(
                    tipo_plano=plano_data["tipo_plano"],
                    valor=plano_data["valor"],
                    duracao_dias=plano_data["duracao_dias"]
                )
                db.add(novo_plano)
                print(f"Plano '{plano_data['tipo_plano']}' criado com sucesso.")
            else:
                print(f"Plano '{plano_data['tipo_plano']}' já existe. Pulando.")
        
        # 4. Comita todas as mudanças de uma vez
        db.commit()
        print("\nSeeding da tabela de Planos concluído.")

    except Exception as e:
        print(f"Ocorreu um erro durante o seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_plans()