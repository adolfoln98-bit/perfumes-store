import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

if DB_URL is None:
    raise ValueError("""La variable de entorno 'DATABASE_URL' no está definida. 
                     Comprueba que existe en el archivo .env y que contiene una URL de conexión válida.""")

def get_connection():
    return psycopg.connect(DB_URL)