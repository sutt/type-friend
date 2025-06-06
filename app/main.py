from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")

SECRET_SPELL = "abc"
user_key_buffers = {}
user_access_granted = {}

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

class KeyPressEvent(BaseModel):
    key: str
    uuid: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main HTML page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/keypress")
async def log_keypress(event: KeyPressEvent):
    """
    Receives keypress events from the client and checks for the secret spell.
    """
    client_uuid = event.uuid
    current_buffer = user_key_buffers.get(client_uuid, [])
    current_buffer.append(event.key)

    current_buffer = current_buffer[-len(SECRET_SPELL):]
    user_key_buffers[client_uuid] = current_buffer

    logger.info(f"Key pressed: {event.key} from UUID: {client_uuid}. Buffer: {''.join(current_buffer)}")

    response_message = {"message": f"Key '{event.key}' received"}

    if "".join(current_buffer) == SECRET_SPELL:
        user_access_granted[client_uuid] = True
        logger.info(f"Secret spell '{SECRET_SPELL}' cast successfully by UUID: {client_uuid}")
        response_message["spell_successful"] = True
        response_message["message"] = f"Key '{event.key}' received. Spell '{SECRET_SPELL}' cast successfully!"
    else:
        response_message["spell_successful"] = False

    return response_message

@app.get("/protected_resource")
async def get_protected_resource(request: Request, session_id: str = None): # Expect session_id as query param
    """
    A protected resource, accessible only if the correct spell was cast by the session.
    """
    if session_id is None:
        logger.warning(f"Access attempt to /protected_resource without session_id from {request.client.host}")
        raise HTTPException(status_code=401, detail="Session ID required")

    has_access = user_access_granted.get(session_id, False)

    if not has_access:
        logger.warning(f"Access denied to /protected_resource for session_id: {session_id} from {request.client.host}")
        raise HTTPException(status_code=403, detail="Access denied. Cast the secret spell correctly.")

    logger.info(f"Access granted to /protected_resource for session_id: {session_id} from {request.client.host}")
    return {"message": "Welcome to the protected resource! You cast the spell correctly."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
