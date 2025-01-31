# auth.py

from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    SecurityScopes,
)
from .hashing import Hasher
from cicloapi.schemas.user_schema import UserInDB
from cicloapi.schemas.token_schema import Token, TokenData
from cicloapi.core.config import settings
import jwt
import logging

router = APIRouter()
logger = logging.getLogger('uvicorn.error')

# Creates a Bearer scheme for authentication with OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=settings.SCOPES)


#################################
# Functions for token management
#################################


def create_token(data: dict, expiration: timedelta | None = None) -> str:
    """
    Creates a token given a dictionary of data.

    Parameters:
        data (dict): Dictionary to encode
        expiration (timedelta|None, optional): Default value is None. Time allowed for the token to exist. If None, it defaults to 15 minutes.

    Returns:
        str: Encoded token
    """

    to_encode = data.copy()
    logger.info(settings.SECRET_KEY)
    if expiration:
        exp = datetime.now(timezone.utc) + expiration
    else:
        exp = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": exp})
    encoded_token = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    logger.info(encoded_token)
    return encoded_token


def check_token(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
) -> str:
    """
    Confirms whether the token is valid or has expired.

    Parameters:
        token (str): Encoded JWT token

    Returns:
        str: Input token

    """
    # We start by writing an exception to use later
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials.",
        headers={"WWW-Authenticate": authenticate_value},
    )

    # We read the token and check if it is correct
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except:
        raise credentials_exception

    # We now check the scopes if any
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        token_scopes = payload.get("scopes", [])
        token_data.scopes = TokenData(scopes=token_scopes)

        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions.",
                    headers={"WWW-Authenticate": authenticate_value},
                )

    return payload


def check_superuser(payload: Annotated[dict, Depends(check_token)]):
    """
    Confirms whether the user has superuser rights.

    Parameters:
        payload (dict): Decoded JWT token


    """
    if not payload["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions.",
            headers={"WWW-Authenticate": f"Bearer scope=superuser"},
        )


#################################
# Endpoints
#################################

# POST request for authentification and handling the token (in JWT format))


@router.post("/token")
async def token_request(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    Function wrapping the login and authorization process.

    Parameters:
        form_data (OAuth2PasswordRequestForm): Username and password obtained through a request form in Ouath2.

    Returns:
        Token: Object made with the token schema, containing the encoded token and its type.

    """

    # We query the username in the DB
    user_dict = settings.USERS_DB.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # We also check validity of the scopes
    requested_scopes = set(form_data.scopes)
    defined_scopes = set(settings.SCOPES.keys())

    if not requested_scopes.issubset(defined_scopes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user rights.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # We now create an object user which stores the user data and we hash the password introduced by the user
    user = UserInDB(**user_dict)

    # Checks the password against the one stored in the DB
    if not Hasher.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # And we now generate the token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={
            "user": user.username,
            "scopes": form_data.scopes,
            "is_superuser": user.is_superuser,
        },
        expiration=access_token_expires,
    )
    token = Token(access_token=access_token, token_type="bearer")

    return token
