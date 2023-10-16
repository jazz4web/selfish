from datetime import datetime, timedelta

from jwt import decode as jwtdecode, encode as jwtencode, PyJWTError


async def check_token(config, token):
    try:
        cache = jwtdecode(
            token, config.get('SECRET_KEY'), algorithms=['HS256'])
    except PyJWTError:
        return None
    return cache


async def create_login_token(request, remember_me, cache):
    if remember_me:
        delta = timedelta(seconds=30*24*60*60)
    else:
        delta = timedelta(seconds=2*60*60)
    d = {'cache': cache, 'exp': datetime.utcnow() + delta}
    return jwtencode(
        d, request.app.config.get('SECRET_KEY'), algorithm='HS256')
