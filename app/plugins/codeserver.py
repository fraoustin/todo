import os
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


def codeServerMiddleware(prefix='127.0.0.1:8080'):
    CODESERVER_PREFIX = prefix

    class RootPathMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            if not request.url.path.startswith('/_nicegui'):
                request.scope["root_path"] = CODESERVER_PREFIX
            response = await call_next(request)
            return response

    return RootPathMiddleware
