import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from key_buffer_manager import KeyBufferManager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

load_dotenv(dotenv_path=os.path.join(PARENT_DIR, ".env"))

SECRET_SPELL_FROM_ENV = os.getenv("APP_SECRET_SPELL", "")
PARSED_SECRET_SPELL = (
    [key.strip() for key in SECRET_SPELL_FROM_ENV.split(",") if key.strip()]
    if SECRET_SPELL_FROM_ENV
    else []
)

if not PARSED_SECRET_SPELL:
    logger.warning(
        "APP_SECRET_SPELL is not defined, is empty, or contains only delimiters. "
        "The spell casting feature will be disabled as no valid spell sequence is configured."
    )
else:
    logger.info(f"Loaded PARSED_SECRET_SPELL: {PARSED_SECRET_SPELL}")

key_buffer_manager = KeyBufferManager(parsed_secret_spell=PARSED_SECRET_SPELL)
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
    current_buffer = key_buffer_manager.add_key(user_uuid=event.uuid, key=event.key)

    logger.info(
        f"Key pressed: {event.key} from UUID: {event.uuid}. Buffer: {current_buffer}"
    )

    response_message = {"message": f"Key '{event.key}' received"}

    if key_buffer_manager.check_spell(user_uuid=event.uuid):
        user_access_granted[event.uuid] = True
        response_message["spell_successful"] = True
        response_message["message"] = (
            f"Key '{event.key}' received. Spell cast successfully!"
        )
        logger.info(f"Secret spell cast successfully by UUID: {event.uuid}")
    else:
        response_message["spell_successful"] = False

    return response_message


@app.get("/protected_resource")
async def get_protected_resource(
    request: Request, session_id: str = None
):  # Expect session_id as query param
    """
    A protected resource, accessible only if the correct spell was cast by the session.
    """
    if session_id is None:
        logger.warning(
            f"Access attempt to /protected_resource without session_id from {request.client.host}"
        )
        raise HTTPException(status_code=401, detail="Session ID required")

    has_access = user_access_granted.get(session_id, False)

    if not has_access:
        logger.warning(
            f"Access denied to /protected_resource for session_id: {session_id} from {request.client.host}"
        )
        raise HTTPException(
            status_code=403, detail="Access denied. Cast the secret spell correctly."
        )

    logger.info(
        f"Access granted to /protected_resource for session_id: {session_id} from {request.client.host}"
    )
    return {
        "message": "Welcome to the protected resource! You cast the spell correctly."
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
