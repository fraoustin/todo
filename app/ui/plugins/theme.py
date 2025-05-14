import hashlib
from urllib.parse import urlencode

from contextlib import contextmanager
from nicegui import ui, app

from .login import current_user


class Gravatar(ui.avatar):

    sizes = {'xs': 18, 'sm': 24, 'md': 32, 'lg': 38, 'xl': 46}

    def __init__(self, email, default='mp', *args, **kw):
        ui.avatar.__init__(self, *args, **kw)
        self.default = default
        self.email = email

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        self._default = value
        if getattr(self, '_email', False) is not False:
            self.email = self.email

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        size = self.sizes.get(self._props.get('size', 'md'), 32)
        self._email = value
        email_encoded = value.lower().encode('utf-8')
        email_hash = hashlib.sha256(email_encoded).hexdigest()
        query_params = urlencode({'s': size, 'd': self.default})
        self._path_image = f"https://www.gravatar.com/avatar/{email_hash}?{query_params}"
        if getattr(self, '_image', False) is not False:
            self._image.source = self._path_image
        else:
            with self:
                self._image = ui.image(self._path_image)


def addnull():
    pass


class Tooltip(ui.tooltip):

    def __init__(self, *args, **kw):
        ui.tooltip.__init__(self, *args, **kw)
        self.classes('text-body1 max-lg:hidden')


class ButtonForInput(ui.button):

    def __init__(self, input, *args, **kw):
        ui.button.__init__(self, *args, **kw)
        self._input = input

    @property
    def value(self):
        return self._input.value

    @value.setter
    def set_value(self, value):
        self._input.value = value


class InputWithButton(ui.input):

    def __init__(self, icon, *args, **kw):
        ui.input.__init__(self, *args, **kw)
        with self.classes('text-body1 flex-grow').props('borderless') as inputbox:
            self._button = ButtonForInput(inputbox, icon=icon).classes('text-h5').props('flat dense').bind_visibility_from(inputbox, 'value')

    def on(self, action, dest, *args, **kw):
        ui.input.on(self, action, dest, *args, **kw)
        if action == 'keydown.enter':
            self._button.on('click', dest)
        return self


@contextmanager
def frame(me, current_route):
    def logout():
        ui.navigate.to('/login')

    def dark_mode_full():
        app.storage.user['dark_mode'] = dark_mode.value
        if dark_mode.value is True:
            ui.colors(primary='white')
            header.classes('q-dark-page', remove='bg-grey-1')
            footer.classes('q-dark-page', remove='bg-grey-1')
            left_drawer.classes('q-dark-page')
        else:
            ui.colors(primary='black')
            header.classes('bg-grey-1', remove='q-dark-page')
            footer.classes('bg-grey-1', remove='q-dark-page')
            left_drawer.classes(remove='q-dark-page')

    ui.add_css('''
    .q-dark-page {
        background: var(--q-dark-page);
    }
    ''')
    dark_mode = ui.dark_mode(False, on_change=dark_mode_full)
    # dark_mode = ui.dark_mode().bind_value(app.storage.user, 'dark_mode')
    ui.colors(primary='black')
    with ui.left_drawer(top_corner=True, bottom_corner=True).style('overflow: hidden;white-space: nowrap').props('bordered').props('width') as left_drawer:
        with ui.row().classes('items-center cursor-pointer py-2').on('click', lambda: (ui.navigate.to('/'), )):
            ui.icon("checklist").classes('text-2xl')
            ui.label("Todo").classes('lg:hidden')
        with ui.list().classes('flex-grow w-full'):
            pass
        with ui.list().classes('flex-grow w-full').classes('lg:hidden').style('width: 80vw'):
            pass
        with ui.list().classes('w-full'):
            with ui.row().classes('items-center cursor-pointer py-2').on('click', lambda: (ui.navigate.to('/settings'), )):
                ui.icon("manage_accounts").classes('text-2xl')
                ui.label("Settings").classes('lg:hidden')
            with ui.row().classes('items-center cursor-pointer py-2').on('click', lambda: (ui.navigate.to('/me'), )):
                ui.icon("face").classes('text-2xl')
                ui.label(me.username).classes('lg:hidden')
            with ui.row().classes('items-center cursor-pointer py-2').on('click', lambda: (ui.navigate.to('/login'), )):
                ui.icon("logout").classes('text-2xl')
                ui.label("Exit").classes('lg:hidden')

    with ui.header().classes('items-center q-pa-sm bg-grey-1').classes('lg:hidden') as header:
        ui.button(on_click=lambda: left_drawer.show() if current_route == '/' else ui.navigate.to('/'), icon='checklist').props('flat round')
        ui.label("Todo").classes('grow  text-primary  text-center')
        ui.button(on_click=lambda: (ui.navigate.to('/me'), ), icon='face').props('flat round')

    with ui.footer().classes('items-center q-pa-sm bg-grey-1').classes('lg:hidden') as footer:
        pass
    with ui.element().classes('lg:pl-[56px] w-full flex justify-center') as content:
        pass

    dark_mode.value = app.storage.user.get('dark_mode', False)
    yield left_drawer, header, footer, content, dark_mode
