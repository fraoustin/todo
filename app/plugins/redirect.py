from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from urllib.parse import urlencode

def redirect(app, prefix_src="/api/latest", prefix_dst="/api/v1", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]):

    @app.api_route(prefix_src + "/{path:path}", methods=methods, include_in_schema=False)
    async def redirect_to_prefix_dst(path: str, request: Request):
        query_string = request.url.query
        new_url = f"{prefix_dst}/{path}"
        if query_string:
            new_url += f"?{query_string}"
        return RedirectResponse(
            url=new_url,
            status_code=307  # Temporary redirect, preserves method and body
        )
