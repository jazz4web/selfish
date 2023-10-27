from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import (
    average, fix_extra_permissions, groups, permissions, roots)
from ..auth.cu import checkcu
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import filter_target_user
from .redi import assign_cache, change_udata
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
            if res['ch-perms']:
                res['perms'] = [name.lower() for name in permissions._fields]
            await conn.close()
            return JSONResponse(res)
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Действие требует авторизации.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        target = await filter_target_user(request, conn, d.get('user'))
        if target is None:
            res['message'] = f'{d.get("user")}? Такого пользователя у нас нет.'
            await conn.close()
            return JSONResponse(res)
        if cu['username'] != target['username'] and \
                (permissions.ADMINISTER in cu['permissions'] or
                 (permissions.CHUROLE in cu['permissions'] and
                  permissions.CHUROLE not in target['permissions']) or
                 (cu['group'] == groups.keeper and
                  target['group'] != groups.keeper and
                  permissions.ADMINISTER not in target['permissions'])):
            chquery = 'UPDATE users SET permissions = $1 WHERE username = $2'
            data = f'data:{target.get("uid")}'
            if int(d.get('nologin', '0')):
                await conn.execute(
                    chquery, [permissions.NOLOGIN], target['username'])
                await change_udata(
                    request.app.rc, data, [permissions.NOLOGIN])
            elif int(d.get('administer', '0')):
                await conn.execute(
                    chquery, roots, target['username'])
                await change_udata(
                    request.app.rc, data, roots)
            else:
                extra = await fix_extra_permissions(
                    cu, target['permissions'])
                assigned = list()
                for each in average:
                    if int(d.get(each, '0')):
                        assigned.append(average[each])
                if (permissions.CHUROLE in assigned or
                    permissions.BLOCK in assigned) \
                            and permissions.FOLLOW not in assigned:
                    assigned.append(permissions.FOLLOW)
                assigned = assigned + extra
                await conn.execute(
                    chquery, assigned or [permissions.NOLOGIN],
                    target['username'])
                await change_udata(
                    request.app.rc, data,
                    assigned or [permissions.NOLOGIN])
            await conn.close()
            await set_flashed(
                request, f'Разрешения {target["username"]} успешно изменены.')
            res['done'] = True
            return JSONResponse(res)
        res['message'] = 'У Вас недостаточно прав.'
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
