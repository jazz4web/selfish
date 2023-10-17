from ..api.tokens import check_token


async def checkcu(request, token):
    cache = await check_token(request.app.config, token)
    if cache:
        data = await request.app.rc.hgetall(cache.get('cache'))
        if data:
            query = await request.app.rc.hgetall(f'data:{data["id"]}')
            if query:
                return {'id': int(query.get('id')),
                        'username': query.get('username'),
                        'registered': query.get('registered'),
                        'last_published': query.get('last_published'),
                        'permissions': query.get('permissions').split(','),
                        'ava': request.url_for(
                            'ava', username=query.get('username'),
                            size=22)._url,
                        'brkey': data.get('brkey')}
    return None
