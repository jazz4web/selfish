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

from .api.auth import GetPasswd, Login, Logout, LogoutAll, ResetPasswd
from .api.main import Captcha, Index, Profile
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


class J2Templates(Jinja2Templates):
    def _create_env(self, directory: str) -> "jinja2.Environment":
        @jinja2.pass_context
        def url_for(
                context: dict, name: str, **path_params: typing.Any) -> str:
            request = context["request"]
            return request.url_for(name, **path_params)

        loader = jinja2.FileSystemLoader(directory)
        assets_env = AssetsEnvironment(static, '/static')
        assets_env.debug = settings.get('ASSETS_DEBUG', bool)
        env = jinja2.Environment(
            loader=loader, autoescape=True, extensions=[assets])
        env.assets_environment = assets_env
        env.globals["url_for"] = url_for
        return env


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
                Route('/reset-passwd', ResetPasswd, name='aresetpwd')]),
            Mount('/static', app=StaticFiles(directory=static),name='static')],
    middleware=middleware,
    exception_handlers=errs)
app.config = settings
app.jinja = J2Templates(directory=templates)
app.rc = aioredis.from_url(settings.get('REDI'), decode_responses=True)
