# importing all the required modules
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

# jwt configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# hashing password
def hash_password(password: str):

    return pwd_context.hash(password)


# verifying password
def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# creating jwt access token
def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# decoding jwt token
def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )