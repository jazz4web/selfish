import asyncio
import functools
import os

from minify_html import minify
from starlette.exceptions import HTTPException
from starlette.responses import (
    FileResponse, HTMLResponse, PlainTextResponse, Response)

from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..errors import E404
from .pg import check_state
from .tools import resize


async def show_picture(request):
    cu = int((await request.app.rc.hgetall(
        request.session.get('_uid', 'empty'))).get('id', '0'))
    conn = await get_conn(request.app.config)
    target = await conn.fetchrow(
        '''SELECT albums.state, albums.author_id, pictures.suffix,
                  pictures.picture, pictures.format FROM albums, pictures
             WHERE pictures.suffix = $1
             AND albums.id = pictures.album_id''',
            request.path_params.get('suffix'))
    base = os.path.dirname(os.path.dirname(__file__))
    if target is None:
        response = FileResponse(
            os.path.join(base, 'static', 'images', '404.png'))
        response.headers.append(
            'cache-control',
            'max-age=0, no-store, no-cache, must-revalidate')
    else:
        if await check_state(conn, target, cu):
            response = Response(
                target.get('picture'),
                media_type=f'image/{target.get("format").lower()}')
            response.headers.append(
                'cache-control',
                'public, max-age={0}'.format(
                    request.app.config.get(
                        'SEND_FILE_MAX_AGE', cast=int, default=0)))
        else:
            response = FileResponse(
                os.path.join(base, 'static', 'images', '403.png'))
            response.headers.append(
                'cache-control',
                'max-age=0, no-store, no-cache, must-revalidate')
    await conn.close()
    return response


async def show_profile(request):
    interval = request.app.config.get('REQUEST_INTERVAL', cast=float)
    html = minify(
        request.app.jinja.get_template(
            'main/profile.html').render(
            request=request, username=request.path_params.get('username'),
            interval=interval, flashed=await get_flashed(request)),
        minify_js=True, remove_processing_instructions=True,
        do_not_minify_doctype=True, keep_spaces_between_attributes=True)
    return HTMLResponse(html)


async def show_avatar(request):
    size = request.path_params['size']
    if size < 22 or size > 160:
        raise HTTPException(status_code=404, detail=E404)
    conn = await get_conn(request.app.config)
    res = await conn.fetchrow(
        'SELECT id, username FROM users WHERE username = $1',
        request.path_params['username'])
    if res is None:
        raise HTTPException(status_code=404, detail=E404)
    ava = await conn.fetchval(
        'SELECT picture FROM avatars WHERE user_id = $1', res.get('id'))
    await conn.close()
    loop = asyncio.get_running_loop()
    image = await loop.run_in_executor(
        None, functools.partial(resize, size, ava))
    response = Response(image, media_type='image/png')
    if ava is None:
        response.headers.append('cache-control', 'public, max-age=0')
    else:
        response.headers.append(
            'cache-control',
            'public, max-age={0}'.format(
                request.app.config.get(
                    'SEND_FILE_MAX_AGE', cast=int, default=0)))
    return response


async def show_robots(request):
    return PlainTextResponse('User-agent: *\nDisallow: /')


async def show_favicon(request):
    if request.method == 'GET':
        return FileResponse(
            os.path.join(os.path.dirname(os.path.dirname(__file__)),
            'static', 'images', 'favicon.ico'))


async def show_index(request):
    interval = request.app.config.get('REQUEST_INTERVAL', cast=float)
    html = minify(
        request.app.jinja.get_template(
            'main/index.html').render(
            request=request, flashed=await get_flashed(request),
            interval=interval),
        minify_js=True, remove_processing_instructions=True,
        do_not_minify_doctype=True, keep_spaces_between_attributes=True)
    return HTMLResponse(html)
