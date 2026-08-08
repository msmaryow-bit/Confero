from fastapi import FastAPI, Response, Request, Form
from fastapi.templating import Jinja2Templates
import json
from starlette.responses import HTMLResponse

templates = Jinja2Templates(directory='templates')
app = FastAPI()
USERS_JSON = 'users.json'
ROOMS_JSON = 'rooms.json'


@app.post('/login')
async def login(request: Request, mail: str = Form(...), password: str = Form(...)):
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        users = json.load(f)

@app.post('/register')
async def register(request: Request, mail: str = Form(...), password: str = Form(...)):
    return render_template('register.html')

@app.post('/login')
async def login(request: Request, mail: str = Form(...), password: str = Form(...)):
    return render_template('login.html')

@app.post('/main')
async def main(request: Request, mail: str = Form(...), password: str = Form(...)):
    return render_template('main.html')
        



