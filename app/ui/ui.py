from fastapi import FastAPI, Request
from nicegui import app, ui
from nicegui.element import Element

from .plugins.login import uilogin, require_auth, current_user, require_admin, UserList
from .plugins.theme import frame, InputWithButton, Gravatar
from .elements import TodoLine, TodoList


def init(fastapi_app, mount_path='/', app_prefix="", secret='your-secret'):
    @ui.page('/login')
    def login(request: Request):
        uilogin(base_url=str(request.url)[:-len('/login')] + app_prefix)

    @ui.page('/settings')
    @require_auth()
    @require_admin()
    async def settings(request: Request):
        me = current_user.get()
        current_route = '/' + str(request.url).split('/')[-1].split('?')[0]
        
        with frame(me, current_route)  as (left_drawer, header, footer, content, dark_mode):
            with content:
                with ui.element('div').classes('w-full').style('min-width: 80%;max-width: 768px;margin: auto;'):
                    ui.label('Utilisateurs:').classes('flex items-center')
                    userlist = UserList(f"{me.api_base}", me.headers)
                    await userlist.load_data()

    @ui.page('/me')
    @require_auth()
    async def admin(request: Request):
        me = current_user.get()
        current_route = '/' + str(request.url).split('/')[-1].split('?')[0]
        
        with frame(me, current_route)  as (left_drawer, header, footer, content, dark_mode):
            with content:
                with ui.column():
                    Gravatar(me.email, size='xl').style('margin: auto;')
                    with ui.grid(columns=2).classes('w-auto'):
                        ui.label('Name:').classes('flex items-center')
                        ui.input(value=me.username).props('dense unfilled borderless').on('change', lambda e: me.update('name', e.sender.value))
                        ui.label('Email').classes('flex items-center')
                        ui.input(value=me.email).props('dense unfilled borderless').on('change', lambda e: me.update('email', e.sender.value))
                        ui.label('Admin').classes('flex items-center')
                        ui.checkbox(value=me.isadmin).props('disable').props('color=black')
                        ui.label('Dark mode').classes('flex items-center')
                        ui.checkbox().props('color=black').bind_value(dark_mode)
    @ui.page('/')
    @require_auth()
    async def main(request: Request):
        me = current_user.get()
        current_route = '/' + str(request.url).split('/')[-1].split('?')[0]

        async def handle_add(event):
            if event.sender.value.strip():
                await todolist.add_todo(event.sender.value)
                event.sender.value = ''
        
        with frame(me, current_route)  as (left_drawer, header, footer, content, dark_mode):
            with content:
                with ui.element('div').classes('w-full').style('min-width: 80%;max-width: 768px;margin: auto;'):
                    input = InputWithButton(icon='o_arrow_circle_down', placeholder='Nouvelle todo').classes('flex-grow w-full').on('keydown.enter', handle_add)
                    input._props['data-id'] = 'onlylg'
                    todolist = TodoList(f"{me.api_base}/latest", me.headers)
                    await todolist.load_data()

            with footer:
                InputWithButton(icon='o_arrow_circle_up', placeholder='Nouvelle todo').on('keydown.enter', handle_add)
            
        ui.add_body_html('''
        <script>
        function updateView() {
            const isDesktop = window.innerWidth >= 1024;
            const onlylgLabel = document.querySelector('[data-id="onlylg"]').closest('label');
            if (onlylgLabel) {
                onlylgLabel.style.display = isDesktop ? 'inline-block' : 'none';
            }
        }
        window.addEventListener('resize', updateView);
        window.addEventListener('load', updateView);
        </script>
        ''')

    ui.run_with(
        fastapi_app,
        mount_path=mount_path,
        storage_secret=secret,
    )