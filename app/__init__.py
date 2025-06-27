from flask import Flask
from flask_login import LoginManager
import os

app = Flask(__name__, template_folder='templates') 
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-flask')
login_manager = LoginManager(app)


from app import route
from app import funcionario