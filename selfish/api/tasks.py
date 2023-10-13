from ..common.pg import get_conn

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
