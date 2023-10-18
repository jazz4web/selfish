from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import permissions
from ..auth.cu import checkcu
from ..common.pg import get_conn
from .pg import filter_target_user
from .redi import assign_cache
from .tools import check_profile_permissions, render_menu


class Profile(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token')),
               'user': None}
        username = request.query_params.get('username')
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        await render_menu(request, res)
        if cu and username:
            conn = await get_conn(request.app.config)
            target = await filter_target_user(request, conn, username)
            if target is None:
                res['message'] = f'{username}? Такого пользователя у нас нет.'
                await conn.close()
                return JSONResponse(res)
            if target and target['uid'] != cu.get('id') and \
                    permissions.FOLLOW not in cu['permissions']:
                res['message'] = 'Для вас доступ закрыт, увы.'
                await conn.close()
                return JSONResponse(res)
            res['user'] = target
            await check_profile_permissions(request, cu, target, res)
            if res['address']:
                res['user']['address'] = await conn.fetchval(
                    'SELECT address FROM accounts WHERE user_id = $1',
                    res['user'].get('uid'))
            await conn.close()
            return JSONResponse(res)
        return JSONResponse(res)


class Captcha(HTTPEndpoint):
    async def get(self, request):
        conn = await get_conn(request.app.config)
        captcha = await conn.fetchrow(
            'SELECT val, suffix FROM captchas ORDER BY random() LIMIT 1')
        res = await assign_cache(
            request.app.rc, 'captcha:',
            captcha.get('suffix'), captcha.get('val'), 180)
        url = request.url_for('captcha', suffix=captcha.get('suffix'))._url
        return JSONResponse({'captcha': res,
                             'url': url})


class Index(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token'))}
        await render_menu(request, res)
        return JSONResponse(res)
