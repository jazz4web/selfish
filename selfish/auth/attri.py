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
