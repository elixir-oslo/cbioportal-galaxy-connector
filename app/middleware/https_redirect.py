from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.requests import Request

class CustomHTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.scheme == "http":
            url = request.url.replace(scheme="https")
            if request.method == "POST":
                return RedirectResponse(url, status_code=307)
            return RedirectResponse(url, status_code=301)
        return await call_next(request)