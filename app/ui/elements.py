from nicegui import ui
from nicegui.element import Element
from pydantic import parse_obj_as
import httpx
from .schemas import Todo


class TodoLine(Element):
    def __init__(self, todo: Todo):
        super().__init__('div')
        self.classes('w-full')
        self.todo = todo

        with self:
            with ui.row().classes('items-center gap-4 w-full'):
                self.checkbox = ui.checkbox(value=todo.terminated, on_change=self.on_change_terminated).props('dense')
                self.input = ui.input(value=todo.text, on_change=self.on_change_text).props('dense borderless readonly').classes('flex-1').style('text-decoration: line-through;' if self.todo.terminated else 'text-decoration: none;')
                ui.button(icon="o_delete", on_click=self.on_delete).props('dense flat round')

    async def on_change_terminated(self):
        self.todo.terminated = self.checkbox.value
        if self.todo.terminated:
            self.input.props['readonly'] = True
            self.input.style('text-decoration: line-through;')
        else:
            self.input.props['readonly'] = False
            self.input.style('text-decoration: none;')
        await self.todo.update()

    async def on_change_text(self):
        self.todo.text = self.input.value
        await self.todo.update()

    async def on_delete(self):
        await self.todo.delete()
        self.delete()


class TodoList(Element):
    def __init__(self, api_base, headers):
        super().__init__('div')
        self.api_base = api_base
        self.headers = headers
        self.classes('column gap-2')

    async def load_data(self):
        with self:
            todos = await Todo.all(self.api_base, self.headers)
            for todo in todos:
                TodoLine(todo)

    async def add_todo(self, text):
        new_todo = await Todo.new(text, self.api_base, self.headers)
        if new_todo:
            with self:
                TodoLine(new_todo)
