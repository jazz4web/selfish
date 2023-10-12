from datetime import datetime

from passlib.hash import pbkdf2_sha256

from ..common.pg import get_conn
from .attri import initials, permissions

async def insert_permissions(config):
    conn = await get_conn(config)
    current = await conn.fetch('SELECT * FROM permissions')
    if current:
        for each in current:
            rem = each.get('permission')
            if rem not in permissions:
                await conn.execute(
                    'DELETE FROM permissions WHERE permission = $1', rem)
    for permission, name in zip(permissions, permissions._fields):
        p = await conn.fetchrow(
            'SELECT * FROM permissions WHERE permission = $1', permission)
        if p is None:
            await conn.execute(
                '''INSERT INTO permissions (permission, name, init)
                     VALUES ($1, $2, $3)''',
                permission,
                name.lower().replace('_', '-'),
                initials.get(permission, False))
    await conn.close()


async def check_username(config, username):
    conn = await get_conn(config)
    res = await conn.fetchrow(
        'SELECT username FROM users WHERE username = $1', username)
    await conn.close()
    return bool(res)


async def check_address(config, address):
    res = False
    conn = await get_conn(config)
    account = await conn.fetchrow(
        'SELECT address, user_id FROM accounts WHERE address = $1', address)
    swap = await conn.fetchrow(
        'SELECT swap FROM accounts WHERE swap = $1', address)
    await conn.close()
    if (account and account.get('user_id')) or swap:
        res = True
    return res


async def update_account(conn, address, uid, now):
    account = await conn.fetchrow(
        'SELECT * FROM accounts WHERE address = $1', address)
    if account:
        await conn.execute(
            '''UPDATE accounts
                 SET address = $1, requested = $2 WHERE user_id = $3''',
            address, now, uid)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, requested, user_id)
                 VALUES ($1, $2, $3)''',
            address, now, uid)


async def create_user_record(
        conn, username, passwd, permissions, now):
    await conn.execute(
        '''INSERT INTO users
           (username, registered, last_visit, password_hash, permissions)
           VALUES ($1, $2, $3, $4, $5)''',
        username, now, now, pbkdf2_sha256.hash(passwd), permissions)
    return await conn.fetchval(
        'SELECT id FROM users WHERE username = $1', username)


async def create_user(config, username, address, passwd, perms):
    now = datetime.utcnow()
    conn = await get_conn(config)
    user_id = await create_user_record(conn, username, passwd, perms, now)
    await update_account(conn, address, user_id, now)
    await conn.close()
