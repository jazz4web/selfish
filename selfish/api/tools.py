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
        menu['profile_url'] = request.url_for(
            'profile', username=cu.get('username'))._url


async def check_profile_permissions(request, cu, user, data):
    data['owner'] = cu.get('id') == user.get('uid')
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
