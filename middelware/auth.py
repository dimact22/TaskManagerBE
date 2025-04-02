# Import the googlemaps library and dotenv to load environment variables
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import HTTPBearer for authorization and token handling
security = HTTPBearer()

# Middleware to extract and return the email from the token payload
async def auth_middleware_status_return(request: Request):
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        # Decode the JWT token using the secret key and HS256 algorithm
        payload = jwt.decode(token, os.getenv("SecretJwt"), algorithms=["HS256"])
        # Return email from the payload
        return str(payload.get("status"))
    except JWTError:
        # Raise an HTTP 403 error if the token is invalid or expired
        raise HTTPException(
            status_code=403, detail="Token is invalid or expired")
    except Exception as e:
        # Raise an HTTP 404 error for any other exceptions
        raise HTTPException(status_code=404, detail="Some error")

async def auth_middleware_phone_return(request: Request):
    """
    Middleware для перевірки JWT токена та отримання номера телефону користувача.

    Args:
        request (Request): HTTP-запит з заголовком Authorization.

    Returns:
        str: Номер телефону користувача, який міститься в токені.

    Raises:
        HTTPException: Якщо токен недійсний або строк дії закінчився (403 FORBIDDEN).
        HTTPException: Якщо сталася інша помилка (404 NOT FOUND).
    """
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        # Decode the JWT token using the secret key and HS256 algorithm
        payload = jwt.decode(token, os.getenv("SecretJwt"), algorithms=["HS256"])
        # Return email from the payload
        return str(payload.get("sub"))
    except JWTError:
        # Raise an HTTP 403 error if the token is invalid or expired
        raise HTTPException(
            status_code=403, detail="Token is invalid or expired")
    except Exception as e:
        # Raise an HTTP 404 error for any other exceptions
        raise HTTPException(status_code=404, detail="Some error")

async def verify_admin_token(request: Request):
    """
    Verifies if the user is an admin.

    Decodes the JWT token and checks if the user is an admin 
    by validating the 'sub' field. Raises 403 if not authorized.

    Parameters:
    - **request**: The incoming HTTP request.

    Returns:
    - If the token is valid and the user is an admin, stores the payload in `request.state.user`.
    """
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv("SecretJwt"), algorithms=["HS256"])
        
        # Check if the user is an admin
        if payload.get("status") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
        request.state.user = payload  # Store the payload for further use
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is invalid or expired.")
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Authorization error: {str(e)}")