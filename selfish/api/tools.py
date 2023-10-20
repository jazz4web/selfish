from ..auth.attri import groups, permissions


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
