from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse


class Index(HTTPEndpoint):
    async def get(self, request):
        res = {'cu': None}
        return JSONResponse(res)
