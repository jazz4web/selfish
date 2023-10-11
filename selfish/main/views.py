import os

from minify_html import minify
from starlette.responses import FileResponse, HTMLResponse, PlainTextResponse

from ..common.flashed import get_flashed


async def show_robots(request):
    return PlainTextResponse('User-agent: *\nDisallow: /')


async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(os.path.dirname(os.path.dirname(__file__)),
            'static', 'images', 'favicon.ico'))


async def show_index(request):
    html = minify(
        request.app.jinja.get_template(
            'main/index.html').render(
            request=request, flashed=await get_flashed(request)),
        minify_js=True, remove_processing_instructions=True,
        do_not_minify_doctype=True, keep_spaces_between_attributes=True)
    return HTMLResponse(html)
