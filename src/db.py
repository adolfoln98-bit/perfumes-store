import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("""La variable de entorno 'DATABASE_URL' no está definida. 
                     Comprueba que existe en el archivo .env y que contiene una URL de conexión válida.""")

engine = create_engine(DATABASE_URL)

session_factory = sessionmaker(bind=engine)

def get_session():
    return session_factory()
