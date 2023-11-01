from minify_html import minify
from starlette.responses import HTMLResponse

from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from .attri import status


async def show_albums(request):
    html = minify(
        request.app.jinja.get_template(
            'pictures/albums.html').render(
            request=request,
            status=status,
            page=await parse_page(request),
            flashed=await get_flashed(request)),
        minify_js=True, remove_processing_instructions=True,
        do_not_minify_doctype=True, keep_spaces_between_attributes=True)
    return HTMLResponse(html)
