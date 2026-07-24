from db import get_session
from sqlalchemy import text


with get_session() as session:
    query= text("SELECT CURRENT_TIMESTAMP;")
    resultado = session.execute(query)
    print(resultado.scalar())
    