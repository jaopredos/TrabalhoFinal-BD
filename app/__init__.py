from flask import Flask
from flask_login import LoginManager

app = Flask(__name__, template_folder='templates') 
login_manager = LoginManager(app)

from app import route
from app import cliente
from app import funcionario
from app import main