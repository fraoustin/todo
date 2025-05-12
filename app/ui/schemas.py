from api.v1.schemas import TodoOut
from pydantic import parse_obj_as
import httpx
from .deps import NotifyingHttpClient

class Todo(TodoOut):

    api_base: str = ''
    headers: str = ''
    
    @classmethod
    async def all(cls, api_base: str, headers: dict):
        async with NotifyingHttpClient() as client:
            response = await client.get(f'{api_base}/todos', headers=headers)
            if response.status_code == 200:
                todos = parse_obj_as(list[Todo], response.json())
                for todo in todos:
                    todo.api_base = api_base
                    todo.headers = headers
                return todos
            else:
                return []
    
    @classmethod
    async def new(cls, text: str, api_base: str, headers: dict):
        async with NotifyingHttpClient() as client:
            response = await client.post(f'{api_base}/todo', headers=headers, json={"text": text})
            if response.status_code == 200:
                todo = parse_obj_as(Todo, response.json())
                todo.api_base = api_base
                todo.headers = headers
                return todo
            else:
                return None

    async def update(self):
        async with NotifyingHttpClient() as client:
            await client.put(
                f"{self.api_base}/todo/{self.id}",
                json={"text": self.text, "terminated": self.terminated},
                headers=self.headers,
                follow_redirects=True
            )

    async def delete(self):
        async with NotifyingHttpClient() as client:
            await client.delete(f"{self.api_base}/todo/{self.id}", headers=self.headers)