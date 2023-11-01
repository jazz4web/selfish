from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import permissions
from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.pg import get_conn
from .pg import check_last, get_user_stat, select_albums
from .tools import render_menu

class Albums(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': await checkcu(
            request, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        await render_menu(request, res)
        if permissions.PICTURE not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        page = await parse_page(request)
        conn = await get_conn(request.app.config)
        last = await check_last(
            conn, page,
            request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3),
            'SELECT count(*) FROM albums WHERE author_id = $1', cu.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        res['pagination'] = await select_albums(
            conn, cu.get('id'), page,
            request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3),
            last)
        if res['pagination']:
            res['html'] = {'albums': request.app.jinja.get_template(
                'pictures/albums-list.html').render(
                request=request, pagination=res['pagination'])}
            if res['pagination']['next'] or res['pagination']['prev']:
                res['html']['pv'] = request.app.jinja.get_template(
                    'pictures/pv.html').render(
                    request=request, pagination=res['pagination'])
        res['extra'] = res['pagination'] is None or \
                       (res['pagination'] and res['pagination']['page'] == 1)
        res['stat'] = await get_user_stat(conn, cu.get('id'))
        await conn.close()
        return JSONResponse(res)
