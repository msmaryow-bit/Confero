import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import json
from starlette.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

templates = Jinja2Templates(directory='templates')
app = FastAPI()
USERS_JSON = 'users.json'
ROOMS_JSON = 'rooms.json'
sl = {}


class RoomCreate(BaseModel):
    name: str
    capacity: int
    equipment: str
    organization: str = "МТС"


@app.post("/api/rooms")
async def add_room(room: RoomCreate):
    with open(ROOMS_JSON, "r", encoding="utf-8") as file:
        rooms = json.load(file)

    numbers = []

    for room_id in rooms:
        if room_id.startswith("room"):
            number = room_id[4:]

            if number.isdigit():
                numbers.append(int(number))

    next_number = max(numbers, default=0) + 1
    room_id = f"room{next_number}"

    rooms[room_id] = {
        "name": room.name,
        "capacity": room.capacity,
        "inventory": room.equipment,
        "organization": room.organization,
        "bookings": []
    }

    with open(ROOMS_JSON, "w", encoding="utf-8") as file:
        json.dump(
            rooms,
            file,
            indent=4,
            ensure_ascii=False
        )

    return {
        "id": next_number,
        "name": room.name,
        "capacity": room.capacity,
        "equipment": room.equipment,
        "organization": room.organization,
        "bookings": []
    }


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


@app.get("/main", response_class=HTMLResponse)
async def show_main(request: Request):
    return templates.TemplateResponse(
        request,
        "main.html"
    )


@app.get("/api/rooms")
async def get_rooms():
    with open(ROOMS_JSON, "r", encoding="utf-8") as file:
        rooms_data = json.load(file)

    rooms = []

    for index, (room_id, room) in enumerate(
        rooms_data.items(),
        start=1
    ):
        rooms.append({
            "id": index,
            "name": room.get("name", room_id),
            "capacity": room.get("capacity", 0),
            "equipment": room.get("inventory", "—"),
            "organization": room.get("organization", "—"),
            "bookings": room.get("bookings", [])
        })

    return rooms


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
