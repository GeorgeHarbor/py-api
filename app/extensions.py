from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicijalizacija SQLAlchemy objekta za rad sa bazom podataka
db = SQLAlchemy()

# Inicijalizacija JWTManager-a za rad sa JSON Web Tokenima
jwt = JWTManager()

# Inicijalizacija Migrate objekta za rad sa migracijama baze podataka
migrate = Migrate()
