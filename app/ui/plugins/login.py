#!/usr/bin/env python3
from typing import Optional
import collections
import inspect
from functools import wraps

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from nicegui import app, ui
import httpx
from urllib.parse import urljoin

from api.auth.schemas import UserOut
from pydantic import parse_obj_as

from contextvars import ContextVar

current_user: ContextVar = ContextVar("current_user")

from pydantic import parse_obj_as
import httpx
from nicegui.element import Element

from ..deps import NotifyingHttpClient

class User(UserOut):

    api_base: str = ''
    headers: str = ''
    
    @classmethod
    async def all(cls, api_base: str, headers: dict):
        async with NotifyingHttpClient() as client:
            response = await client.get(f'{api_base}/users', headers=headers)
            if response.status_code == 200:
                users = parse_obj_as(list[User], response.json())
                for user in users:
                    user.api_base = api_base
                    user.headers = headers
                return users
            else:
                return []
    
    @classmethod
    async def new(cls, api_base: str, headers: dict, **kw):
        async with NotifyingHttpClient() as client:
            response = await client.post(f'{api_base}/user', headers=headers, json=kw)
            if response.status_code == 200:
                user = parse_obj_as(User, response.json())
                user.api_base = api_base
                user.headers = headers
                return user
            else:
                return None

    async def update(self, key: str, value: dict):
        async with NotifyingHttpClient() as client:
            await client.put(
                f"{self.api_base}/user/{self.id}",
                json={key: value},
                headers=self.headers
            )
            setattr(self, key, value)

    async def delete(self):
        async with NotifyingHttpClient() as client:
            await client.delete(f"{self.api_base}/user/{self.id}", headers=self.headers)


class Me(UserOut):

    api_base: str = ''
    headers: str = ''
    
    @classmethod
    async def get(cls, api_base: str, token: str):
        async with NotifyingHttpClient() as client:
            response = await client.get(f'{api_base}/me', headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                user = parse_obj_as(cls, response.json())
                user.api_base = api_base
                user.headers = {"Authorization": f"Bearer {token}"}
                print(user)
                return user
            else:
                return None
    
    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    async def update(self, key: str, value: dict):
        async with NotifyingHttpClient() as client:
            await client.put(
                f"{self.api_base}/me",
                json={key: value},
                headers=self.headers
            )
            setattr(self, key, value)



async def authenticate(username: str, password: str):
    token_url = app.storage.user['base_url'] + '/api/token'

    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token_data = response.json()
            app.storage.user['token'] = token_data['access_token']
            app.storage.user['username'] = username
            app.storage.user['authenticated'] = True
            ui.notify("Connexion réussie !")
            return True
        return False


def uilogin(base_url):
    async def try_login():
        if await authenticate(username.value, password.value):
            ui.navigate.to('/')
        else:
            ui.notify('Wrong username or password', color='negative')
    
    app.storage.user.clear()
    app.storage.user['base_url'] = base_url
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
    return None


def require_auth(redirect_to='/login'):
    def decorator(page_func):
        if inspect.iscoroutinefunction(page_func):
            @wraps(page_func)
            async def wrapper(*args, **kwargs):
                if not app.storage.user.get('authenticated', False):
                    ui.notify("⛔ Accès refusé, redirection...")
                    ui.navigate.to(redirect_to)
                    return    
                base_url = app.storage.user.get('base_url', '')
                token = app.storage.user.get('token', '')
                me = await Me.get(app.storage.user['base_url']+"/api", app.storage.user['token'])
                current_user.set(me)
                return await page_func(*args, **kwargs)
        else:
            @wraps(page_func)
            def wrapper(*args, **kwargs):
                if not app.storage.user.get('authenticated', False):
                    ui.notify("⛔ Accès refusé, redirection...")
                    ui.navigate.to(redirect_to)
                    return
                return page_func(*args, **kwargs)
        return wrapper
    return decorator


def require_admin(redirect_to='/login'):
    def decorator(page_func):
        if inspect.iscoroutinefunction(page_func):
            @wraps(page_func)
            async def wrapper(*args, **kwargs):
                user = current_user.get()
                if not user.isadmin:
                    ui.notify("⛔ Accès refusé, redirection...")
                    ui.navigate.to(redirect_to)
                    return
                return await page_func(*args, **kwargs)
        else:
            @wraps(page_func)
            def wrapper(*args, **kwargs):
                user = current_user.get()
                if not user.isadmin:
                    ui.notify("⛔ Accès refusé, redirection...")
                    ui.navigate.to(redirect_to)
                    return
                return page_func(*args, **kwargs)
        return wrapper
    return decorator

class UserLine(ui.expansion):
    
    @classmethod
    def get_icon(cls, user: User):
        if user.disabled:
            return "person_off"
        if user.isadmin:
            return "security"
        return "person"

    def __init__(self, user: User, api_base: str, headers: dict, current_user: Me):
        super().__init__(user.username, icon= UserLine.get_icon(user) )
        self.user = user
        self.api_base = api_base
        self.headers = headers

        with self:
            with ui.grid(columns=2).classes('w-auto pl-8'):
                ui.label('Name:').classes('flex items-center')
                ui.input(value=self.user.username).props('dense unfilled borderless').on('change', lambda e: self.user.update('username', e.sender.value))
                ui.label('Email').classes('flex items-center')
                ui.input(value=self.user.email).props('dense unfilled borderless').on('change', lambda e: self.user.update('email', e.sender.value))
                ui.label('Admin').classes('flex items-center')
                elt = ui.checkbox(value=self.user.isadmin).props('color=black').on('change', lambda e: self.user.update('isadmin', e.sender.value))
                if current_user.id == user.id:
                    elt.props('disable')
                ui.label('Actif').classes('flex items-center')
                elt = ui.checkbox(value= not self.user.disabled).props('color=black').on('change', lambda e: self.user.update('disabled', not e.sender.value))
                if current_user.id == user.id:
                    elt.props('disable')
                ui.label('Token').classes('flex items-center')
                ui.label(self.user.token)
                ui.button('Mot de passe', icon='key', color='positive').on('click', lambda: ChangePassword(self.user).open())
                if current_user.id != user.id:
                    ui.button('Supprimer', icon='delete', color='negative').on('click', lambda: self.on_delete())
                else:
                    ui.label('')

    async def on_delete(self):
        await self.user.delete()
        self.delete()


class UserList(Element):
    def __init__(self, api_base: str, headers: str):
        super().__init__('div')
        self.api_base = api_base
        self.headers = headers
        self.classes('column gap-2')
        self.current_user = current_user.get()

        with ui.page_sticky(x_offset=36, y_offset=36):
            ui.button(icon='add', color='positive').props('fab').on('click', lambda: CreateUser(self).open())

    async def load_data(self):
        with self:
            users =  await User.all(self.api_base, self.headers)
            for user in users:
                UserLine(user, self.api_base, self.headers, self.current_user)

    async def add_user(self, **kw):
        new_user = await User.new(self.api_base, self.headers, **kw)
        if new_user:
            with self:
                UserLine(new_user, self.api_base, self.headers, self.current_user)


class ChangePassword(ui.dialog):
    def __init__(self, user, *args, **kw):
        super().__init__(*args, **kw)
        with self, ui.card():
            ui.label('Changer votre mot de passe')
            with ui.grid(columns=2).classes('w-auto'):
                ui.label('Nouveau mot de passe:').classes('flex items-center')
                self.new_password = ui.input(password=True, on_change=lambda: self.check_password()).props('dense')
                ui.label('Répéter').classes('flex items-center')
                self.repeat_password_input = ui.input(password=True, on_change=lambda: self.check_password()).props('dense')
                ui.button('Annuler', icon='cancel', color='negative').on('click', lambda: self.close())
                self.button_change = ui.button('Changer', icon='key', color='positive').on('click', lambda: self.user.update('password', self.repeat_password_input.value))
                self.button_change.disable()

    def check_password(self):
        if len(self.new_password.value) > 0:
            if self.new_password.value == self.repeat_password_input.value:
                self.button_change.enable()
                return
        self.button_change.disable()


class CreateUser(ui.dialog):
    def __init__(self, src, *args, **kw):
        super().__init__(*args, **kw)
        self._src = src
        self._values = {}
        with self, ui.card():
            ui.label("Creation d'un utilisateur")
            with ui.grid(columns=2).classes('w-auto'):
                ui.label('Nom:').classes('flex items-center')
                self._values['username'] = ui.input().props('dense')
                ui.label('Email').classes('flex items-center')
                self._values['email'] = ui.input().props('dense')
                ui.label('Mot de passe').classes('flex items-center')
                self._values['password'] = ui.input(password=True).props('dense')
                ui.label('Admin').classes('flex items-center')
                self._values['isadmin'] = ui.checkbox(value= False).props('color=black')
                ui.label('Seulement API').classes('flex items-center')
                self._values['onlyapi'] = ui.checkbox(value= False).props('color=black')
                ui.button('Annuler', icon='cancel', color='negative').on('click', lambda: self.close())
                self.button_change = ui.button('Créer', icon='add', color='positive').on('click', lambda: self.create())
    
    async def create(self):
        await self._src.add_user(**{elt: self._values[elt].value for elt in self._values})
        self.close()