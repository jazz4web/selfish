from minify_html import minify
from starlette.responses import HTMLResponse


async def show_albums(request):
    html = minify(
        request.app.jinja.get_template(
            'pictures/albums.html').render(
            request=request),
        minify_js=True, remove_processing_instructions=True,
        do_not_minify_doctype=True, keep_spaces_between_attributes=True)
    return HTMLResponse(html)
