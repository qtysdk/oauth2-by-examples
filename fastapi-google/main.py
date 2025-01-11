from typing import Union
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse

config = Config('.env')
app = FastAPI()

# 添加 session 中間件
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# 配置 OAuth
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
    client_id=config.get('client_id'),
    client_secret=config.get('client_secret')

)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = request.session.get('user')
    if user:
        return f"""
        <h1>Hello, {user['email']}</h1>
        <p><a href="/logout">Logout</a></p>
        {user}
        """
    return """
        <h1>Welcome</h1>
        <p>Please <a href="/login">login with Google</a></p>
    """


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')  # 這裡設置回調 URL
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token['userinfo']
    request.session['user'] = dict(userinfo)
    return RedirectResponse(url='/')


@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
