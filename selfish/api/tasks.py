import asyncio
import functools

from ..captcha.common import check_val
from ..captcha.picturize.picture import generate_image
from ..common.pg import get_conn


async def change_pattern(conf, suffix):
    conn = await get_conn(conf)
    val = await check_val(conn)
    loop = asyncio.get_running_loop()
    pic = await loop.run_in_executor(
        None, functools.partial(generate_image, val))
    await conn.execute(
        'UPDATE captchas SET val = $1, picture = $2 WHERE suffix = $3',
        val, pic.read(), suffix)
    await loop.run_in_executor(
        None, functools.partial(pic.close))
    await conn.close()
    return None


async def rem_old_session(request, cache, username):
    conn = await get_conn(request.app.config)
    sessions = await conn.fetchval(
        'SELECT sessions FROM users WHERE username = $1', username) or list()
    sessions.append(cache)
    if len(sessions) > 3:
        old = sessions[0]
        if await request.app.rc.exists(old):
            await request.app.rc.delete(old)
        del sessions[0]
    await conn.execute(
        'UPDATE users SET sessions = $1 WHERE username = $2',
        sessions, username)
    await conn.close()
