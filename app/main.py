import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# print('Hello World')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# XXX: do it better
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

load_dotenv(dotenv_path=os.path.join(PARENT_DIR, ".env"))

# XXX: Load the secret spell from environment variable as a comma-separated string.
# XXX: Default to an empty string if not set.
SECRET_SPELL_FROM_ENV = os.getenv("APP_SECRET_SPELL", "")
# XXX: Parse the comma-separated string into a list of individual key strings.
# XXX: Ensure keys are stripped of whitespace and empty strings (from "key1,,key2") are filtered out.
PARSED_SECRET_SPELL = [key.strip() for key in SECRET_SPELL_FROM_ENV.split(',') if key.strip()] if SECRET_SPELL_FROM_ENV else []
# XXX: Store the number of keys in the secret spell.
SECRET_SPELL_KEY_COUNT = len(PARSED_SECRET_SPELL)

# XXX: Log the parsed spell for debugging.
# XXX: Warn if the spell is effectively empty, as spell casting won't work then.
if not PARSED_SECRET_SPELL:
    logger.warning(
        "APP_SECRET_SPELL is not defined, is empty, or contains only delimiters. "
        "The spell casting feature will be disabled as no valid spell sequence is configured."
    )
else:
    logger.info(f"Secret spell loaded as key sequence: {PARSED_SECRET_SPELL}")

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

    # XXX: Trim the buffer to the length of the number of keys in the secret spell.
    if SECRET_SPELL_KEY_COUNT > 0:
        current_buffer = current_buffer[-SECRET_SPELL_KEY_COUNT:]
    elif SECRET_SPELL_KEY_COUNT == 0:
        # XXX: If the configured spell is empty, the buffer should also be empty.
        current_buffer = []
    # XXX: If SECRET_SPELL_KEY_COUNT is 0 and current_buffer had items,
    # XXX: it will be correctly emptied by the above.
    # XXX: If current_buffer was already shorter than SECRET_SPELL_KEY_COUNT, it's preserved.

    user_key_buffers[client_uuid] = current_buffer

    # XXX: Log the current buffer as a list of keys.
    logger.info(
        f"Key pressed: {event.key} from UUID: {client_uuid}. Buffer: {current_buffer}"
    )

    response_message = {"message": f"Key '{event.key}' received"}

    # XXX: Check if the spell is defined (not empty) and if the current buffer matches the parsed secret spell.
    if PARSED_SECRET_SPELL and current_buffer == PARSED_SECRET_SPELL:
        user_access_granted[client_uuid] = True
        # XXX: Log success with the spell shown as a list of keys.
        logger.info(
            f"Secret spell {PARSED_SECRET_SPELL} cast successfully by UUID: {client_uuid}"
        )
        response_message["spell_successful"] = True
        # XXX: For the user-facing message, show the spell as a comma-joined string for readability.
        response_message["message"] = (
            f"Key '{event.key}' received. Spell '{','.join(PARSED_SECRET_SPELL)}' cast successfully!"
        )
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
