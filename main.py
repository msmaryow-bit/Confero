import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import json
from starlette.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException
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


class BookingCreate(BaseModel):
    date: str
    start: str
    end: str


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


@app.post("/api/rooms/{room_id}/bookings")
async def create_booking(
        room_id: int,
        booking: BookingCreate
):
    try:
        start_time = datetime.strptime(
            booking.start,
            "%H:%M"
        )

        end_time = datetime.strptime(
            booking.end,
            "%H:%M"
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат времени"
        )

    if start_time >= end_time:
        raise HTTPException(
            status_code=400,
            detail="Начало должно быть раньше окончания"
        )

    with open(ROOMS_JSON, "r", encoding="utf-8") as file:
        rooms = json.load(file)

    room_key = f"room{room_id}"

    if room_key not in rooms:
        raise HTTPException(
            status_code=404,
            detail="Комната не найдена"
        )

    room = rooms[room_key]
    bookings = room.setdefault("bookings", [])

    for old_booking in bookings:
        if old_booking["date"] != booking.date:
            continue

        old_start = datetime.strptime(
            old_booking["start"],
            "%H:%M"
        )

        old_end = datetime.strptime(
            old_booking["end"],
            "%H:%M"
        )

        has_intersection = (
                start_time < old_end
                and end_time > old_start
        )

        if has_intersection:
            raise HTTPException(
                status_code=409,
                detail="Комната уже забронирована на это время"
            )

    booking_id = max(
        [item.get("id", 0) for item in bookings],
        default=0
    ) + 1

    new_booking = {
        "id": booking_id,
        "date": booking.date,
        "start": booking.start,
        "end": booking.end,
        "participants": []
    }

    bookings.append(new_booking)

    with open(ROOMS_JSON, "w", encoding="utf-8") as file:
        json.dump(
            rooms,
            file,
            indent=4,
            ensure_ascii=False
        )

    return new_booking


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


@app.delete("/api/rooms/{room_id}/bookings/{booking_id}")
async def cancel_booking(room_id: int, booking_id: int):
    with open(ROOMS_JSON, "r", encoding="utf-8") as f:
        rooms = json.load(f)

    room_key = f"room{room_id}"
    if room_key not in rooms:
        raise HTTPException(404, "Комната не найдена")

    bookings = rooms[room_key].get("bookings", [])
    for i, b in enumerate(bookings):
        if b.get("id") == booking_id:
            del bookings[i]
            with open(ROOMS_JSON, "w", encoding="utf-8") as f:
                json.dump(rooms, f, indent=4, ensure_ascii=False)
            return {"ok": True}

    raise HTTPException(404, "Бронирование не найдено")


@app.get("/main", response_class=HTMLResponse)
async def show_root2(request: Request):
    return templates.TemplateResponse(request, "main.html")


@app.get("/bookings", response_class=HTMLResponse)
async def show_root2(request: Request):
    return templates.TemplateResponse(request, "bookings.html")


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

    result = []

    for room_key, room in rooms_data.items():
        number = room_key.replace("room", "")

        if not number.isdigit():
            continue

        result.append({
            "id": int(number),
            "name": room.get("name", room_key),
            "capacity": room.get("capacity", 0),
            "equipment": room.get("inventory", "—"),
            "organization": room.get("organization", "—"),
            "bookings": room.get("bookings", [])
        })

    return result


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
