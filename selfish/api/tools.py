async def render_menu(request, data):
    menu = {'cu': bool(data['cu'])}
    data['menu'] = menu
