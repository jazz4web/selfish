import asyncio

from ..api.tasks import ping_user
from ..api.tokens import check_token
from ..auth.attri import get_group, permissions
from ..common.flashed import set_flashed


async def checkcu(request, token):
    cache = await check_token(request.app.config, token)
    if cache:
        data = await request.app.rc.hgetall(cache.get('cache'))
        if data:
            query = await request.app.rc.hgetall(f'data:{data["id"]}')
            uid = int(query.get('id'))
            if query and permissions.NOLOGIN in query.get('permissions'):
                await request.app.rc.delete(cache.get('cache'))
                await request.app.rc.delete(f'data:{uid}')
                await set_flashed(
                    request, 'Ваше присутствие в сервисе нежелательно.')
                return None
            if query:
                asyncio.ensure_future(
                    ping_user(request.app.config, uid))
                return {'id': uid,
                        'username': query.get('username'),
                        'group': await get_group(query.get('permissions')),
                        'registered': query.get('registered'),
                        'last_published': query.get('last_published'),
                        'permissions': query.get('permissions').split(','),
                        'ava': request.url_for(
                            'ava', username=query.get('username'),
                            size=22)._url,
                        'brkey': data.get('brkey')}
    return None
