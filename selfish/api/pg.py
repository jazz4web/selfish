import math

from datetime import datetime, timedelta

from validate_email import validate_email

from ..auth.attri import get_group, permissions
from ..common.aparsers import iter_pages, parse_title, parse_units
from ..common.random import get_unique_s


async def get_album(conn, uid, suffix):
    query = await conn.fetchrow(
        '''SELECT id, title, created, suffix, state, volume FROM albums
             WHERE suffix = $1 AND author_id = $2''',
        suffix, uid)
    if query:
        num = await conn.fetchval(
            'SELECT count(*) FROM pictures WHERE album_id = $1',
            query.get('id'))
        return {'id': query.get('id'),
                'title': query.get('title'),
                'created': f'{query.get("created").isoformat()}Z',
                'suffix': query.get('suffix'),
                'state': query.get('state'),
                'volume_': query.get('volume'),
                'volume': await parse_units(query.get('volume')),
                'files': num,
                'parse_t': len(query.get('title')) > 50,
                'parsed22': await parse_title(query.get('title'), 22),
                'parsed36': await parse_title(query.get('title'), 36),
                'parsed50': await parse_title(query.get('title'), 50)}
    return None


async def create_new_album(conn, uid, title, state):
    now = datetime.utcnow()
    suffix = await get_unique_s(conn, 'albums', 8)
    empty = await conn.fetchval(
        'SELECT id FROM albums WHERE author_id IS NULL')
    if empty:
        await conn.execute(
            '''UPDATE albums SET title = $1,
                                 created = $2,
                                 changed = $2,
                                 suffix = $3,
                                 state = $4,
                                 volume = 0,
                                 author_id = $5 WHERE id = $6''',
            title, now, suffix, state, uid, empty)
    else:
        await conn.execute(
            '''INSERT INTO
                 albums (title, created, changed, suffix, state, author_id)
                 VALUES ($1, $2, $2, $3, $4, $5)''',
            title, now, suffix, state, uid)
    return suffix


async def get_user_stat(conn, uid):
    return {'albums': await conn.fetchval(
        'SELECT count(*) FROM albums WHERE author_id = $1', uid),
            'files': await conn.fetchval(
        '''SELECT count(*) FROM albums, pictures
             WHERE author_id = $1
             AND pictures.album_id = albums.id''', uid),
            'volume': await parse_units(await conn.fetchval(
        'SELECT sum(volume) FROM albums WHERE author_id = $1', uid) or 0)}


async def select_albums(conn, uid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT title, suffix FROM albums
             WHERE author_id = $1
             ORDER BY changed DESC LIMIT $2 OFFSET $3''',
        uid, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'albums': [{'title': record.get('title'),
                            'parsed': await parse_title(
                                record.get('title'), 40),
                            'suffix': record.get('suffix')}
                           for record in query]}
    return None


async def check_last(conn, page, per_page, *args):
    num = await conn.fetchval(*args)
    return math.ceil(num / per_page) or 1


async def check_rel(conn, uid1, uid2):
    friend = bool(await conn.fetchrow(
        '''SELECT author_id, friend_id FROM friends
             WHERE author_id = $1 AND friend_id = $2''', uid1, uid2))
    follower = bool(await conn.fetchrow(
        '''SELECT author_id, follower_id FROM followers
             WHERE author_id = $1 AND follower_id = $2''', uid1, uid2))
    blocker = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid2, uid1))
    blocked = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid1, uid2))
    return {'friend': friend, 'follower': follower,
            'blocker': blocker, 'blocked': blocked}


async def check_account(config, conn, account, address):
    length = timedelta(
        seconds=round(3600*config.get('TOKEN_LENGTH', cast=float)))
    interval = timedelta(
        seconds=round(3600*config.get('REQUEST_INTERVAL', cast=float)))
    if datetime.utcnow() - account.get('requested') < interval:
        return 'Сервис временно недоступен, попробуйте зайти позже.'
    if account.get('address') == address:
        return 'Задан Ваш текущий адрес, запрос не имеет смысла.'
    if await check_swap(conn, address, length):
        return 'Адрес в свопе, выберите другой или повторите попытку позже.'
    requested = await conn.fetchrow(
        'SELECT requested, user_id FROM accounts WHERE address = $1', address)
    if requested and requested.get('user_id'):
        return 'Этот адрес уже зарегистрирован, запрос отклонён.'
    if requested and datetime.utcnow() - requested.get('requested') < length:
        return 'Адрес регистрируется, выберите другой или попробуйте позже.'
    return None


async def get_acc(conn, account, address):
    now = datetime.utcnow()
    if account:
        address = account.get('address')
        await conn.execute(
            '''UPDATE accounts SET swap = null, requested = $1
                 WHERE address = $2''', now, address)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, requested)
                 VALUES ($1, $2)''', address, now)
    return await conn.fetchrow(
        'SELECT id, address, user_id FROM accounts WHERE address = $1',
        address)


async def define_acc(conn, account):
    if account and account.get('user_id'):
        username = await conn.fetchval(
            'SELECT username FROM users WHERE id = $1', account.get('user_id'))
        return username, 'Сброс забытого пароля', 'emails/resetpwd.html'
    return 'Гость', 'Регистрация', 'emails/invitation.html'


async def check_swap(conn, address, length):
    swapped = await conn.fetchrow(
        'SELECT id, swap, requested FROM accounts WHERE swap = $1', address)
    if swapped:
        if datetime.utcnow() - swapped.get('requested') > length:
            await conn.execute(
                'UPDATE accounts SET swap = null WHERE id = $1',
                swapped.get('id'))
            return None
        else:
            return True


async def check_address(request, conn, address):
    message = None
    interval = timedelta(
        seconds=round(
            3600*request.app.config.get('REQUEST_INTERVAL', cast=float)))
    length = timedelta(
        seconds=round(
            3600*request.app.config.get('TOKEN_LENGTH', cast=float)))
    acc = await conn.fetchrow(
        'SELECT address, requested, user_id FROM accounts WHERE address = $1',
        address)
    if acc and datetime.utcnow() - acc.get('requested') < interval:
        message = 'Сервис временно недоступен, попробуйте зайти позже.'
    if await check_swap(conn, address, length):
        message = 'Адрес в свопе, выберите другой или повторите попытку позже.'
    return message, acc


async def filter_target_user(request, conn, username):
    query = await conn.fetchrow(
        '''SELECT id, username, registered, last_visit, permissions,
                  description, last_published FROM users
             WHERE username = $1''', username)
    if query:
        return {'uid': query.get('id'),
                'username': query.get('username'),
                'group': await get_group(query.get('permissions')),
                'registered': f'{query.get("registered").isoformat()}Z',
                'last_visit': f'{query.get("last_visit").isoformat()}Z',
                'permissions': query.get('permissions'),
                'description': query.get('description'),
                'last_published': f'{query.get("last_published").isoformat()}Z'
                if query.get('last_published') else None,
                'ava': request.url_for(
                    'ava', username=query.get('username'), size=160)._url}


async def filter_user(conn, login):
    squery = '''SELECT users.id, users.username,
                       users.password_hash, users.permissions,
                       users.last_published, users.registered
                  FROM users, accounts
                    WHERE users.id = accounts.user_id '''
    if validate_email(login):
        squery += ' AND accounts.address = $1'
    else:
        squery += ' AND users.username = $1'
    query = await conn.fetchrow(squery, login)
    if query and permissions.NOLOGIN not in query.get('permissions'):
        return {'id': query.get('id'),
                'username': query.get('username'),
                'password_hash': query.get('password_hash'),
                'registered': query.get('registered'),
                'last_published': query.get('last_published'),
                'permissions': query.get('permissions')}
