from validate_email import validate_email

from ..auth.attri import permissions


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
