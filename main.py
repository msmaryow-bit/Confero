import os
from fastapi import FastAPI, Response, Request, Form
from fastapi.templating import Jinja2Templates
import json
from starlette.responses import HTMLResponse

templates = Jinja2Templates(directory='templates')
app = FastAPI()

sl = {}


@app.get("/register", response_class=HTMLResponse)
async def show_root(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/login", response_class=HTMLResponse)
async def show_root1(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/main", response_class=HTMLResponse)
async def show_root2(request: Request):
    return templates.TemplateResponse(request, "main.html")


@app.post('/register', response_class=HTMLResponse)
async def register(request: Request, name: str = Form(...),
                   email: str = Form(...),
                   password: str = Form(...),
                   organization: str = Form(...)):
    with open('users.json', 'w', encoding='utf-8') as users:
        sl[email] = {'name': name, 'password': password, 'organization': organization}
        users.write(json.dumps(sl, indent=4, ensure_ascii=False))
    return templates.TemplateResponse(request, "main.html")


@app.on_event('startup')
async def startup():
    global sl
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as users:
            sl = json.loads(users.read())
    else:
        sl = {}
