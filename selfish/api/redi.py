from ..common.random import randomize


async def get_unique(conn, prefix, num):
    while True:
        res = prefix + await randomize(num)
        if await conn.exists(res):
            continue
        return res


async def assign_uid(request, prefix, remember_me, user, brkey):
    if remember_me:
        expiration = request.app.config.get('SESSION_LIFETIME')
    else:
        expiration = 2 * 60 * 60
    cache = await get_unique(request.app.rc, prefix, 9)
    await request.app.rc.hmset(cache, {'id': user.get('id'), 'brkey': brkey})
    await request.app.rc.expire(cache, expiration)
    data = f'data:{user.get("id")}'
    existed = await request.app.rc.exists(data)
    await request.app.rc.hmset(
        data, {'id': user.get('id'),
               'username': user.get('username'),
               'registered': f"{user.get('registered').isoformat()}Z",
               'last_published': f"{user.get('last_published').isoformat()}Z"
               if user.get('last_published') else 0,
               'permissions': ','.join(user.get('permissions')),
               'many': 0})
    if existed:
        await request.app.rc.hset(data, key='many', value=1)
        if remember_me:
            await request.app.rc.persist(data)
            await request.app.rc.expire(data, expiration)
        else:
            if await request.app.rc.ttl(data) < expiration:
                await request.app.rc.persist(data)
                await request.app.rc.expire(data, expiration)
    else:
        await request.app.rc.expire(data, expiration)
    return cache


async def extract_cache(rc, cache):
    suffix, val = await rc.hmget(cache, 'suffix', 'val')
    return suffix, val


async def get_unique(conn, prefix, num):
    while True:
        res = prefix + await randomize(num)
        if await conn.exists(res):
            continue
        return res


async def assign_cache(rc, prefix, suffix, val, expiration):
    cache = await get_unique(rc, prefix, 6)
    await rc.hmset(cache, {'suffix': suffix, 'val': val})
    await rc.expire(cache, expiration)
    return cache
