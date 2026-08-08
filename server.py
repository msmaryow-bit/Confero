from fastapi import FastAPI, Response, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
import json
from starlette.responses import HTMLResponse

templates = Jinja2Templates(directory='templates')
app = FastAPI()
USERS_JSON = 'users.json'
ROOMS_JSON = 'rooms.json'


@app.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse(request, 'login.html')


@app.post("/login")
async def do_login(response: Response, mail: str = Form(...), password: str = Form(...)):
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        users = json.load(f)
    if mail not in users or users[mail]["password"] != password:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
