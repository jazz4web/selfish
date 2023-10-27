from collections import namedtuple

USER_PATTERN = r'^[A-ZА-ЯЁa-zа-яё][A-ZА-ЯЁa-zа-яё0-9\-_.]{2,15}$'

Perm = namedtuple(
    'Perm',
    ['NOLOGIN',
     'READ',
     'FOLLOW',
     'LIKE',
     'PM',
     'COMMENT',
     'ALIAS',
     'ART',
     'BLOCK',
     'CHUROLE',
     'PICTURE',
     'ANNOUNCE',
     'ADMINISTER'])

permissions = Perm(
    NOLOGIN='заблокирован',
    READ='читать блоги',
    FOLLOW='создавать ленту',
    LIKE='ставить лайки/дизлайки',
    PM='писать в приват',
    COMMENT='комментировать блоги',
    ALIAS='создавать алиасы для ссылок',
    ART='вести свой блог',
    BLOCK='литовать блоги и комментарии',
    CHUROLE='назначать разрешения',
    PICTURE='хранить изображения',
    ANNOUNCE='делать объявления',
    ADMINISTER='без ограничений')

initials = {permissions.READ: True,
            permissions.FOLLOW: True,
            permissions.LIKE: True,
            permissions.PM: True,
            permissions.COMMENT: True,
            permissions.ALIAS: True,
            permissions.ART: True}

roots = [permission for permission in permissions
         if permission != permissions.NOLOGIN]
average = {name.lower(): permission
    for name, permission in zip(permissions._fields, permissions)
    if permission != permissions.NOLOGIN and
    permission != permissions.ADMINISTER}
curators = (permissions.NOLOGIN,
            permissions.READ,
            permissions.FOLLOW,
            permissions.LIKE,
            permissions.PM,
            permissions.COMMENT,
            permissions.ALIAS,
            permissions.ART)
keepers = curators + (permissions.BLOCK, permissions.CHUROLE)

Group = namedtuple('Group', ['pariah',
                             'taciturn',
                             'commentator',
                             'blogger',
                             'curator',
                             'keeper',
                             'root'])

groups = Group(pariah="Изгои",
               taciturn="Читатели",
               commentator="Комментаторы",
               blogger="Писатели",
               curator="Модераторы",
               keeper="Хранители",
               root="Администраторы")


async def get_group(perms):
    if permissions.ADMINISTER in perms:
        return groups.root
    if permissions.ART in perms \
            and permissions.PICTURE in perms \
            and permissions.ANNOUNCE in perms \
            and permissions.CHUROLE in perms:
        return groups.keeper
    if permissions.BLOCK in perms:
        return groups.curator
    if permissions.ART in perms \
            or permissions.ANNOUNCE in perms \
            or permissions.PICTURES in perms:
        return groups.blogger
    if permissions.LIKE in perms \
            or permissions.COMMENT in perms \
            or permissions.PM in perms:
        return groups.commentator
    if permissions.READ in perms:
        return groups.taciturn
    if permissions.NOLOGIN in perms:
        return groups.pariah


async def fix_extra_permissions(user, current):
    if user['group'] == groups.keeper:
        return [permission for permission in current
                if permission not in keepers]
    if user['group'] == groups.curator:
        return [permission for permission in current
                if permission not in curators]
    return []
