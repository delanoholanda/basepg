import os
from urllib.parse import quote_plus

class Config:

    password = quote_plus('SuaSenha')

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'postgresql://usuario:{password}@host/database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False