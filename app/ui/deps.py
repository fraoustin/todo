import httpx
from nicegui import ui

class NotifyingHttpClient:
    def __init__(self, ):
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(follow_redirects=True)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()

    async def get(self, url, **kwargs):
        return await self._request(self.client.get, url, **kwargs)

    async def post(self, url, **kwargs):
        return await self._request(self.client.post, url, **kwargs)

    async def put(self, url, **kwargs):
        return await self._request(self.client.put, url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self._request(self.client.delete, url, **kwargs)

    async def _request(self, method, url, **kwargs):
        response = await method(url, **kwargs)
        if response.status_code != 200:
            ui.notify(
                f"Erreur {response.status_code} sur {url}",
                type='negative'
            )
        return response
