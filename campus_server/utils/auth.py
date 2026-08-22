import datetime
import jwt
import bcrypt
from django.conf import settings

def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def gen_token(payload: dict) -> str:
    exp = datetime.datetime.utcnow() + datetime.timedelta(days=settings.JWT_EXPIRE_DAYS)
    data = {**payload, "exp": exp}
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
