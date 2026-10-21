import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError
from exceptions import auth


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    raise ValueError(
        "La variable SECRET_KEY no está definida."
    )

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))

ALGORITHM = "HS256"

def crear_access_token(user_id: int, duracion=ACCESS_TOKEN_EXPIRE_MINUTES) ->str:
    expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=duracion
    )

    payload = {
        "sub": str(user_id),
        "exp": expiracion,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require_exp": True}
            )
    except JWTError:
        raise auth.TokenInvalidoError("Token invalido")

    user_id = payload.get("sub")

    if user_id is None:
        raise auth.TokenInvalidoError("Token invalido")

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise auth.TokenInvalidoError("Token invalido")

    return {
        "id": user_id,
    }
