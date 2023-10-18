from validate_email import validate_email

from ..auth.attri import get_group, permissions


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
