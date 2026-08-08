import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import json
from starlette.responses import HTMLResponse, RedirectResponse

templates = Jinja2Templates(directory='templates')
app = FastAPI()
USERS_JSON = 'users.json'
ROOMS_JSON = 'rooms.json'
sl = {}


@app.get("/login")
async def get_login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "error": None,
            "mail": ""
        }
    )


@app.post("/login")
async def do_login(
        request: Request,
        mail: str = Form(...),
        password: str = Form(...)
):
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        users = json.load(f)

    if mail in users and users[mail]["password"] == password:
        return RedirectResponse(
            url="/main",
            status_code=303
        )

    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "error": "Неправильная почта или пароль",
            "mail": mail
        }
    )


@app.get("/register", response_class=HTMLResponse)
async def show_root(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/main", response_class=HTMLResponse)
async def show_root2(request: Request):
    return templates.TemplateResponse(request, "main.html")


@app.post('/register', response_class=HTMLResponse)
async def register(name: str = Form(...),
                   email: str = Form(...),
                   password: str = Form(...),
                   organization: str = Form(...)):
    with open('users.json', 'w', encoding='utf-8') as users:
        sl[email] = {'name': name, 'password': password, 'organization': organization}
        users.write(json.dumps(sl, indent=4, ensure_ascii=False))


@app.on_event('startup')
async def startup():
    global sl
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as users:
            sl = json.loads(users.read())
    else:
        sl = {}
