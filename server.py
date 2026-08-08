from fastapi import FastAPI, Response, Request, Form
from fastapi.templating import Jinja2Templates
import json
from starlette.responses import HTMLResponse

templates = Jinja2Templates(directory='templates')
app = FastAPI()


@app.post('/login')
async def login(request: Request, mail: str = Form(...), password: str = Form(...)):

