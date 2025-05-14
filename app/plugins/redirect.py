from fastapi.responses import RedirectResponse
from fastapi import Request
from typing import List


def redirect(app, prefix_src="/api/latest", prefix_dst="/api/v1", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]):

    @app.api_route(prefix_src + "/{path:path}", methods=methods, include_in_schema=False)
    async def redirect_to_prefix_dst(path: str, request: Request):
        return RedirectResponse(
            url=f"{prefix_dst}/{path}",
            status_code=307
        )
