import os

import jinja2
import typing

from redis import asyncio as aioredis
from starlette.applications import Starlette
from starlette.config import Config
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import assets

from .api.auth import (
    ChangeAva, ChangeEmail, ChangePasswd, GetPasswd,
    Login, Logout, LogoutAll, RequestEm,
    RequestPasswd, ResetPasswd)
from .api.main import Captcha, Index, Profile
from .api.tasks import check_swapped
from .captcha.views import show_captcha
from .errors import show_error
from .main.views import (
    show_avatar, show_favicon, show_index, show_profile, show_robots)

base = os.path.dirname(__file__)
static = os.path.join(base, 'static')
templates = os.path.join(base, 'templates')
settings = Config(os.path.join(os.path.dirname(base), '.env'))

try:
    from .addenv import SITE_NAME, SITE_DESCRIPTION, MAIL_PASSWORD
    if SITE_NAME:
        settings.file_values["SITE_NAME"] = SITE_NAME
    if SITE_DESCRIPTION:
        settings.file_values["SITE_DESCRIPTION"] = SITE_DESCRIPTION
    if MAIL_PASSWORD:
        settings.file_values["MAIL_PASSWORD"] = MAIL_PASSWORD
except ModuleNotFoundError:
    pass

DI = '''typing.Union[str, os.PathLike[typing.AnyStr],
typing.Sequence[typing.Union[str,
os.PathLike[typing.AnyStr]]]]'''.replace('\n', ' ')


class J2Templates(Jinja2Templates):
    def _create_env(
            self,
            directory: DI, **env_options: typing.Any) -> "jinja2.Environment":
        loader = jinja2.FileSystemLoader(directory)
        assets_env = AssetsEnvironment(static, '/static')
        assets_env.debug = settings.get('ASSETS_DEBUG', bool)
        env_options.setdefault("loader", loader)
        env_options.setdefault("autoescape", True)
        env_options.setdefault("extensions", [assets])
        env = jinja2.Environment(**env_options)
        env.assets_environment = assets_env
        return env


async def run_before():
    await check_swapped(settings)


middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings.get('SECRET_KEY'),
        max_age=settings.get('SESSION_LIFETIME', cast=int))]

errs = {403: show_error,
        404: show_error,
        405: show_error}

app = Starlette(
    debug=settings.get('DEBUG', cast=bool),
    routes=[Route('/', show_index, name='index'),
            Route('/favicon.ico', show_favicon, name='favicon.ico'),
            Route('/robots.txt', show_robots, name='robots.txt'),
            Route('/ava/{username}/{size:int}', show_avatar, name='ava'),
            Route('/captcha/{suffix}', show_captcha, name='captcha'),
            Route('/profile/{username}', show_profile, name='profile'),
            Mount('/api', name='api', routes=[
                Route('/index', Index, name='aindex'),
                Route('/captcha', Captcha, name='acaptcha'),
                Route('/login', Login, name='alogin'),
                Route('/logout', Logout, name='alogout'),
                Route('/logout-all', LogoutAll, name='alogoutall'),
                Route('/profile', Profile, name='aprofile'),
                Route('/request-reg', GetPasswd, name='agetpasswd'),
                Route('/reset-passwd', ResetPasswd, name='aresetpwd'),
                Route('/request-passwd', RequestPasswd, name='arequestpwd'),
                Route('/change-ava', ChangeAva, name='chava'),
                Route('/change-passwd', ChangePasswd, name='chpwd'),
                Route('/request-email-change', RequestEm, name='rem-change'),
                Route('/change-email', ChangeEmail, name='change-email')]),
            Mount('/static', app=StaticFiles(directory=static),name='static')],
    on_startup=[run_before],
    middleware=middleware,
    exception_handlers=errs)
app.config = settings
app.jinja = J2Templates(directory=templates)
app.rc = aioredis.from_url(settings.get('REDI'), decode_responses=True)
