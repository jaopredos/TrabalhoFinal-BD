# mainFlask.py (versão corrigida para deploy)
import os
from app import app

if __name__ == '__main__':
    # Render.com fornece a porta através da variável de ambiente 'PORT'.
    # Usamos 5000 como padrão se estivermos rodando localmente.
    port = int(os.environ.get('PORT', 5000))
    
    # O host '0.0.0.0' faz o servidor ser acessível publicamente.
    app.run(host='0.0.0.0', port=port)
    
