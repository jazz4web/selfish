import asyncio

from datetime import datetime
from passlib.hash import pbkdf2_sha256
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from validate_email import validate_email

from ..auth.cu import checkcu
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import check_address, filter_user
from .redi import assign_uid, extract_cache
from .tasks import (
    change_pattern, rem_all_sessions, rem_current_session, rem_old_session,
    request_passwd)
from .tokens import check_token, create_login_token
from .tools import fix_bad_token

BADCAPTCHA = 'Тест провален, либо устарел, попробуйте снова.'
AUTHORIZED = '''Вы авторизованы, действие невозможно, нужно выйти и повторить
переход по ссылке.'''


class ResetPasswd(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': None, 'aid': None}
        auth = request.headers.get('x-auth-token')
        cu = await checkcu(request, auth)
        if cu:
            res['cu'] = cu
            res['message'] = AUTHORIZED
            return JSONResponse(res)
        token = request.headers.get('x-reg-token')
        acc = await check_token(request.app.config, token)
        if acc is None:
            res['message'] = await fix_bad_token(request.app.config)
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        acc = await conn.fetchrow(
            '''SELECT accounts.id, accounts.user_id, accounts.requested,
                      accounts.swap, users.username, users.last_visit
                 FROM accounts, users
                 WHERE accounts.id = $1 AND accounts.user_id = users.id''',
            acc.get('aid'))
        await conn.close()
        if acc is None or acc.get('user_id') is None\
                or acc.get('last_visit') > acc.get('requested') \
                or acc.get('swap'):
            res['message'] = 'Действие невозможно, брелок под сомнением.'
            return JSONResponse(res)
        res['aid'] = acc.get('id')
        res['username'] = acc.get('username')
        return JSONResponse(res)

    async def post(self, request):
        res = {'cu': None, 'done': None}
        d = await request.form()
        address, passwd, confirma, aid = (
            d.get('address'), d.get('passwd'),
            d.get('confirma'), d.get('aid'))
        if not all((address, passwd, confirma, aid)):
            res['message'] = 'Нужно заполнить все поля формы.'
            return JSONResponse(res)
        if passwd != confirma:
            res['message'] = 'Пароли не совпадают.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        acc = await conn.fetchrow(
            '''SELECT a.id, a.address, a.user_id, u.username
                 FROM accounts AS a, users AS u
                 WHERE a.user_id = u.id AND a.id = $1''',
            int(aid))
        if acc.get('address') != address or acc.get('user_id') is None:
            res['message'] = 'Действие невозможно, неверный запрос.'
            await conn.close()
            return JSONResponse(res)
        await conn.execute(
            '''UPDATE users SET password_hash = $1, last_visit = $2
                 WHERE id = $3''',
            pbkdf2_sha256.hash(passwd), datetime.utcnow(), acc.get('user_id'))
        res['done'] = True
        await conn.close()
        await set_flashed(
            request, f'Уважаемый {acc.get("username")}, у Вас новый пароль.')
        return JSONResponse(res)


class GetPasswd(HTTPEndpoint):
    async def post(self, request):
        res = {'cu': None}
        d = await request.form()
        address, cache, captcha = (
            d.get('address'), d.get('cache'), d.get('captcha'))
        if not cache:
            res['message'] = BADCAPTCHA
            return JSONResponse(res)
        suffix, val = await extract_cache(request.app.rc, cache)
        if captcha != val:
            res['message'] = BADCAPTCHA
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        if not validate_email(address):
            res['message'] = 'Нужно ввести адрес электронной почты.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        message, account = await check_address(request, conn, address)
        await conn.close()
        if message:
            res['message'] = message
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        res['done'] = True
        asyncio.ensure_future(
            change_pattern(request.app.config, suffix))
        asyncio.ensure_future(
            request_passwd(request, account, address))
        await set_flashed(
            request, 'На ваш адрес выслано письмо с инструкциями.')
        return JSONResponse(res)


class LogoutAll(HTTPEndpoint):
    async def post(self, request):
        res = {'result': None}
        token = (await request.form()).get('token')
        if token:
            cache = await check_token(request.app.config, token)
            if cache:
                uid = await request.app.rc.hget(cache.get('cache'), 'id')
                cu = await checkcu(request, token)
                if cu.get('id') == int(uid):
                    asyncio.ensure_future(
                        rem_all_sessions(request, cu.get('id')))
                    del request.session['_uid']
                    res['result'] = True
                    await set_flashed(request, f'Пока, {cu["username"]}!')
        return JSONResponse(res)


class Logout(HTTPEndpoint):
    async def post(self, request):
        res = {'result': None}
        token = (await request.form()).get('token')
        if token:
            cache = await check_token(request.app.config, token)
            if cache:
                uid = await request.app.rc.hget(cache.get('cache'), 'id')
                cu = await checkcu(request, token)
                if cu.get('id') == int(uid):
                    await request.app.rc.delete(cache.get('cache'))
                    del request.session['_uid']
                    asyncio.ensure_future(
                        rem_current_session(
                            request.app.config,
                            cache.get('cache'), cu.get('id')))
                res['result'] = True
                await set_flashed(request, f'Пока, {cu["username"]}!')
        return JSONResponse(res)


class Login(HTTPEndpoint):
    async def post(self, request):
        d = await request.form()
        login, passwd, rme, cache, captcha, brkey = (
            d.get('login'), d.get('passwd'),
            int(d.get('rme')), d.get('cache'),
            d.get('captcha'), d.get('brkey'))
        res = {'token': None}
        if not cache:
            res['message'] = BADCAPTCHA
            return JSONResponse(res)
        suffix, val = await extract_cache(request.app.rc, cache)
        if captcha != val:
            res['message'] = BADCAPTCHA
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        user = await filter_user(conn, login)
        await conn.close()
        if user and pbkdf2_sha256.verify(
                passwd, user.get('password_hash')):
            d = await assign_uid(request, 'uid:', rme, user, brkey)
            request.session['_uid'] = d
            res['token'] = await create_login_token(request, rme, d)
            await set_flashed(request, f'Привет, {user.get("username")}!')
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            if rme:
                asyncio.ensure_future(
                    rem_old_session(request, d, user.get('username')))
        else:
            res['message'] = 'Неверный логин или пароль, вход невозможен.'
            return JSONResponse(res)
        return JSONResponse(res)
