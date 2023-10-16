from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
from ..common.pg import get_conn
from .redi import assign_cache
from .tools import render_menu


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
