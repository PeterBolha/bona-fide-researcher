"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
# Decorator for authenticating jwt tokens
from functools import wraps
from http import HTTPStatus

import jwt
from flask import Response, g, request, current_app
from jwt import ExpiredSignatureError, InvalidTokenError

def check_jwt_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        secret_key = current_app.config.get("jwt_secret_key")
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return Response("Authorization header missing.",
                            HTTPStatus.UNAUTHORIZED)

        header_parts = auth_header.split()
        if len(header_parts) != 2 or header_parts[0].lower() != 'bearer':
            return Response("Authorization header has invalid format. Bearer "
                            "token auth expected.", HTTPStatus.UNAUTHORIZED)

        token = header_parts[1]
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            g.jwt_payload = payload
        except ExpiredSignatureError:
            return Response("Authorization token has expired.", HTTPStatus.UNAUTHORIZED)
        except InvalidTokenError:
            return Response("Authorization token is invalid.", HTTPStatus.UNAUTHORIZED)
        except Exception as e:
            return Response(f"Error occurred when verifying authorization "
                            f"token {e}.",
                            HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return wrapper
