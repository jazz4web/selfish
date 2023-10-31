from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.cu import checkcu
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
        return JSONResponse(res)
