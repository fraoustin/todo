import os
from fastapi import FastAPI


from plugins.codeserver import codeServerMiddleware
from plugins.redirect import redirect
from api.auth.api import router as api_auth
from api.v1.api import router as api_v1
from config import get_settings

settings = get_settings()
APP_PORT = os.environ.get('APP_PORT', settings.app_port) #8000
APP_PREFIX = os.environ.get('APP_PREFIX', settings.app_prefix) #"/proxy/%s" % APP_PORT

app = FastAPI(title="Main API Gateway", docs_url="/api/docs", redoc_url="/api/redoc")
app.add_middleware(codeServerMiddleware(prefix=APP_PREFIX))

#API
app.include_router(api_auth, prefix="/api", tags=["Authentication"])
app.include_router(api_v1, prefix="/api/v1", tags=["Version 1"])
redirect(app, "/api/latest", "/api/v1")

#Nicegui
from ui import ui
ui.init(app, app_prefix=APP_PREFIX)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=APP_PORT, reload=True)