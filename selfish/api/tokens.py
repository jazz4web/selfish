from datetime import datetime, timedelta

from jwt import encode as jwtencode


async def create_login_token(request, remember_me, cache):
    if remember_me:
        delta = timedelta(seconds=30*24*60*60)
    else:
        delta = timedelta(seconds=2*60*60)
    d = {'cache': cache, 'exp': datetime.utcnow() + delta}
    return jwtencode(
        d, request.app.config.get('SECRET_KEY'), algorithm='HS256')
