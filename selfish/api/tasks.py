import asyncio
import functools

from datetime import datetime

from aiosmtplib import send
from email.message import EmailMessage

from ..auth.pg import create_user_record
from ..captcha.common import check_val
from ..captcha.picturize.picture import generate_image
from ..common.pg import get_conn
from .pg import define_acc, get_acc
from .tokens import get_request_token
from .tools import define_target_url

remswap = 'UPDATE accounts SET swap = null WHERE id = $1'


async def check_swapped(config):
    conn = await get_conn(config)
    swapped = await conn.fetch(
        'SELECT id, requested FROM accounts WHERE swap IS NOT null')
    length = 3600 * config.get('TOKEN_LENGTH', cast=float)
    now = datetime.utcnow()
    while swapped:
        cur = swapped.pop()
        req = (now - cur.get('requested')).seconds
        if req > length:
            await conn.execute(remswap, cur['id'])
        else:
            asyncio.ensure_future(
                remove_swap_on_startup(config, cur.get('id'), length - req))
    await conn.close()


async def remove_swap_on_startup(config, aid, interval):
    await asyncio.sleep(interval)
    conn = await get_conn(config)
    await conn.execute(remswap, aid)
    await conn.close()


async def remove_swap(config, account):
    await asyncio.sleep(
        3600*config.get('TOKEN_LENGTH', cast=float))
    conn = await get_conn(config)
    await conn.execute(remswap, account.get('id'))
    await conn.close()


async def request_email_change(request, account, address, cu):
    conn = await get_conn(request.app.config)
    requested = await conn.fetchrow(
        'SELECT address, user_id FROM accounts WHERE address = $1', address)
    if requested and not requested.get('user_id'):
        await conn.execute('DELETE FROM accounts WHERE address = $1', address)
    await conn.execute(
        'UPDATE accounts SET swap = $1, requested = $2 WHERE address = $3',
        address, datetime.utcnow(), account.get('address'))
    await conn.close()
    token = await get_request_token(request, account.get('id'))
    url = f'{request.url_for("index")}#change-email/{token}'
    content = request.app.jinja.get_template(
        'emails/change-email.html').render(
            username=cu.get('username'),
            index=request.url_for('index'), target=url,
            length=request.app.config.get('TOKEN_LENGTH', cast=float),
            interval=request.app.config.get('REQUEST_INTERVAL', cast=float),
            old=account.get('address'), new=address)
    if request.app.config.get('DEBUG', cast=bool):
        print(content)
    else:
        message = EmailMessage()
        message["From"] = request.app.config.get('SENDER', cast=str)
        message["To"] = address
        message["Subject"] = request.app.config.get(
            'SUBJECT_PREFIX', cast=str) + "Смена e-mail адреса"
        message.set_content(content)
        message.replace_header('Content-Type', 'text/html; charset="utf-8"')
        await send(
            message,
            recipients=[address],
            hostname=request.app.config.get('MAIL_SERVER', cast=str),
            port=request.app.config.get('MAIL_PORT', cast=str),
            username=request.app.config.get('MAIL_USERNAME', cast=str),
            password=request.app.config.get('MAIL_PASSWORD', cast=str),
            use_tls=request.app.config.get('MAIL_USE_SSL', cast=bool))



async def create_user(config, username, password, aid):
    conn = await get_conn(config)
    now = datetime.utcnow()
    perms = [each.get('permission') for each in await conn.fetch(
        'SELECT permission FROM permissions WHERE init = true')]
    user_id = await create_user_record(conn, username, password, perms, now)
    await conn.execute(
        'UPDATE accounts SET user_id = $1 WHERE id = $2', user_id, aid)
    await conn.close()


async def request_passwd(request, account, address):
    conn = await get_conn(request.app.config)
    username, subject, template = await define_acc(conn, account)
    account = await get_acc(conn, account, address)
    await conn.close()
    url = await define_target_url(
        request, account,
        await get_request_token(request, account.get('id')))
    content = request.app.jinja.get_template(template).render(
        username=username, index=request.url_for('index'),
        target=url, length=request.app.config.get('TOKEN_LENGTH', cast=float),
        interval=request.app.config.get('REQUEST_INTERVAL', cast=float))
    if request.app.config.get('DEBUG', cast=bool):
        print(content)
    else:
        message = EmailMessage()
        message["From"] = request.app.config.get('SENDER', cast=str)
        message["To"] = account.get('address')
        message["Subject"] = request.app.config.get(
            'SUBJECT_PREFIX', cast=str) + subject
        message.set_content(content)
        message.replace_header('Content-Type', 'text/html; charset="utf-8"')
        await send(
            message,
            recipients=[account.get('address')],
            hostname=request.app.config.get('MAIL_SERVER', cast=str),
            port=request.app.config.get('MAIL_PORT', cast=str),
            username=request.app.config.get('MAIL_USERNAME', cast=str),
            password=request.app.config.get('MAIL_PASSWORD', cast=str),
            use_tls=request.app.config.get('MAIL_USE_SSL', cast=bool))
    return None


async def ping_user(config, uid):
    conn = await get_conn(config)
    await conn.execute(
        'UPDATE users SET last_visit = $1 WHERE id = $2',
        datetime.utcnow(), uid)
    await conn.close()


async def rem_all_sessions(request, uid):
    conn = await get_conn(request.app.config)
    sessions = await conn.fetchval(
        'SELECT sessions FROM users WHERE id = $1', uid) or list()
    if sessions:
        for each in range(len(sessions)):
            if await request.app.rc.exists(sessions[each]):
                await request.app.rc.delete(sessions[each])
        await request.app.rc.delete(f'data:{uid}')
        await conn.execute(
            'UPDATE users SET sessions = $1 WHERE id = $2', list(), uid)
    await conn.close()


async def rem_current_session(config, cache, uid):
    conn = await get_conn(config)
    sessions = await conn.fetchval(
        'SELECT sessions FROM users WHERE id = $1', uid) or list()
    if cache in sessions:
        sessions.remove(cache)
        await conn.execute(
            'UPDATE users SET sessions = $1 WHERE id = $2', sessions, uid)
        await conn.close()


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
