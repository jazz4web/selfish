from ..auth.attri import groups, permissions


async def fix_bad_token(config):
    length = config.get('TOKEN_LENGTH')
    return f'Данные устарели, срок действия брелка {length} часов.'


async def define_target_url(request, account, token):
    if account.get('user_id'):
        return f'{request.url_for("index")}#reset-password/{token}'
    return f'{request.url_for("index")}#request-password/{token}'


async def render_menu(request, data):
    menu = {'cu': bool(data['cu'])}
    data['menu'] = menu
    if cu := data['cu']:
        p = data['cu']['permissions']
        menu['tools'] = data['cu'] and \
            (permissions.ALIAS in p or permissions.PICTURE in p or
             permissions.ANNOUNCE in p or permissions.ART in p)
        menu['pictures'] = data['cu'] and permissions.PICTURE in p
        menu['pictures_url'] = request.url_for('pictures:albums')._url
        menu['profile_url'] = request.url_for(
            'profile', username=cu.get('username'))._url


async def check_profile_permissions(request, cu, user, rel, data):
    data['rel'] = rel
    data['owner'] = cu.get('id') == user.get('uid')
    data['acts'] = (permissions.PM in cu['permissions'] and
                    permissions.PM in user['permissions'] and
                    not rel['blocker'] and not rel['blocked']) or \
                   (permissions.BLOCK not in cu['permissions'] and
                    permissions.BLOCK not in user['permissions']) or \
                   (permissions.FOLLOW in user['permissions'] and
                    permissions.PICTURE in cu['permissions'] and
                    not rel['blocked'] and not rel['blocker'])
    data['mfriend'] = permissions.FOLLOW in user['permissions'] and \
            (permissions.PICTURE in cu['permissions'] or
             permissions.ART in cu['permissions']) and \
            not rel['blocker'] and not rel['blocked']
    data['block'] = permissions.BLOCK not in cu['permissions'] and \
            permissions.BLOCK not in user['permissions']
    data['pm'] = permissions.PM in cu['permissions'] and \
            permissions.PM in user['permissions'] and \
            not rel['blocker'] and not rel['blocked']
    data['address'] = cu.get('id') == user.get('uid') or \
            (permissions.ADMINISTER in cu['permissions']
             or cu['group'] == groups.keeper or
             (permissions.CHUROLE in cu['permissions']
              and user['group'] != groups.keeper and
              user['group'] != groups.root))
    data['description'] = (permissions.ART in cu['permissions'] and
                           cu['id'] == user['uid']) or user['description']
    data['ch-perms'] = cu['username'] != user['username'] and \
            (permissions.ADMINISTER in cu['permissions'] or
             (permissions.CHUROLE in cu['permissions'] and
              permissions.CHUROLE not in user['permissions']) or
             (cu['group'] == groups.keeper and
              user['group'] != groups.keeper and
              permissions.ADMINISTER not in user['permissions']))
    if data['ch-perms']:
        data['html'] = request.app.jinja.get_template(
            'main/perms.html').render(
            request=request, cu=cu, user=user,
            permissions=permissions, groups=groups)
