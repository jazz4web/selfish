import os

from starlette.responses import FileResponse, HTMLResponse, PlainTextResponse


async def show_robots(request):
    return PlainTextResponse('User-agent: *\nDisallow: /')


async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(os.path.dirname(os.path.dirname(__file__)),
            'static', 'images', 'favicon.ico'))


async def show_index(request):
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request})
