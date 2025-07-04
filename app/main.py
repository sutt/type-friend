import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from key_buffer_manager import KeyBufferManager
from database import (
    init_db,
    get_session,
    AccessStore,
    SpellIPStore,
)


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

API_DOMAIN = os.getenv("API_DOMAIN", "https://type-friend.com")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    docs_url="/docs" if bool(int(os.getenv("API_DEBUG", 0))) else None,
    openapi_url="/openapi.json" if bool(int(os.getenv("API_DEBUG", 0))) else None,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


_key_buffer_manager_instance = None
_db_session_instance = None
_user_access_granted_instance = None
_successful_spell_ips_instance = None


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """
    Custom 404 Not Found handler.
    """
    logger.info(f"Serving 404 page for path: {request.url.path}")
    context = {
        "request": request,
        "api_domain": API_DOMAIN,
        "og_title": "404 - Page Not Found",
        "og_description": "The page you are looking for does not exist.",
        "og_image": "static/img/gandalf-at-door.jpg",
    }
    return templates.TemplateResponse("404.html", context, status_code=404)


def get_key_buffer_manager() -> KeyBufferManager:
    """
    Dependency that provides the KeyBufferManager singleton instance.
    This ensures state persists across requests.
    """
    global _key_buffer_manager_instance
    if _key_buffer_manager_instance is None:
        _key_buffer_manager_instance = KeyBufferManager(
            parsed_secret_spell=PARSED_SECRET_SPELL
        )
    return _key_buffer_manager_instance


def get_db_session():
    global _db_session_instance
    if _db_session_instance is None:
        init_db()
        _db_session_instance = get_session()
    return _db_session_instance


def get_user_access_state() -> dict:
    """
    Dependency that provides the user access state dictionary.
    This allows for easy testing and state isolation.
    """
    global _user_access_granted_instance
    if _user_access_granted_instance is None:
        _user_access_granted_instance = AccessStore(get_db_session())
    return _user_access_granted_instance


def get_successful_spell_ips_state() -> dict:
    """
    Dependency that provides the successful spell IPs state dictionary.
    This allows for easy testing and state isolation.
    """
    global _successful_spell_ips_instance
    if _successful_spell_ips_instance is None:
        _successful_spell_ips_instance = SpellIPStore(get_db_session())
    return _successful_spell_ips_instance


class KeyPressEvent(BaseModel):
    key: str
    uuid: str


class KeyPressResponse(BaseModel):
    message: str
    spell_successful: bool


class ProtectedResourceResponse(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main HTML page.
    """
    context = {
        "request": request,
        "api_domain": API_DOMAIN,
        "og_title": "Mines of Chaumia",
        "og_description": "The Mines of Chaumia are Open & filled with Treasures",
        "og_image": "static/img/gandalf-at-door.jpg"
    }
    return templates.TemplateResponse("index.html", context)


@app.get("/mines", response_class=HTMLResponse)
async def enter_mines(
    request: Request,
    session_id: str | None = None,
    access_state: dict = Depends(get_user_access_state),
):
    """
    Serves the mines template for users who have successfully cast the spell.
    """
    if not session_id:
        logger.warning(
            f"Access attempt to /mines without session_id from {request.client.host}"
        )
        raise HTTPException(status_code=401, detail="Session ID required")

    has_access = access_state.get(session_id, False)

    if not has_access:
        logger.warning(
            f"Access denied to /mines for session_id: {session_id} from {request.client.host}"
        )
        raise HTTPException(
            status_code=403, detail="Access denied. Cast the secret spell correctly."
        )

    logger.info(
        f"Access granted to /mines for session_id: {session_id} from {request.client.host}"
    )
    context = {
        "request": request,
        "api_domain": API_DOMAIN,
        "og_title": "Mines of Chaumia",
        "og_description": "The Mines of Chaumia are Open & filled with Treasures",
        "og_image": "static/img/gandalf-at-door.jpg"
    }
    return templates.TemplateResponse("mines.html", context)


@app.post("/keypress", response_model=KeyPressResponse)
async def log_keypress(
    request: Request,
    event: KeyPressEvent,
    key_buffer_manager: KeyBufferManager = Depends(get_key_buffer_manager),
    access_state: dict = Depends(get_user_access_state),
    successful_spell_ips: dict = Depends(get_successful_spell_ips_state),
):
    """
    Receives keypress events from the client and checks for the secret spell.
    """
    current_buffer = key_buffer_manager.add_key(user_uuid=event.uuid, key=event.key)

    logger.info(
        f"Key pressed: {event.key} from UUID: {event.uuid}. Buffer: {current_buffer}"
    )

    response_message = {"message": f"Key '{event.key}' received"}

    if key_buffer_manager.check_spell(user_uuid=event.uuid):
        if not (request.client):
            logger.warning(
                "Request.client cannot be identified for successful secret spell cast. "
                f"UUID: {event.uuid}"
            )
            raise HTTPException(
                status_code=403,
                detail="Could not determine request IP; rejecting request.",
            )

        if request.client.host in successful_spell_ips:
            response_message["spell_successful"] = False
            response_message["message"] = (
                f"Key '{event.key}' received. Spell sequence correct, "
                f"but IP {request.client.host} has already cast the spell. "
                "Access not granted for this new session."
            )
            logger.warning(
                f"Spell sequence correct for UUID {event.uuid} from IP {request.client.host}, "
                "but this IP has already cast the spell."
            )
        else:
            successful_spell_ips[request.client.host] = {
                "user_uuid": event.uuid,
                "cast_time": datetime.utcnow(),
            }
            access_state[event.uuid] = True
            response_message["spell_successful"] = True
            response_message["message"] = (
                f"Key '{event.key}' received. Spell cast successfully!"
            )
            logger.info(
                f"Secret spell cast successfully by UUID: {event.uuid} "
                f"from IP: {request.client.host}. Access granted."
            )
    else:
        response_message["spell_successful"] = False

    return response_message


if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG

    api_debug = bool(int(os.getenv("API_DEBUG", False)))
    api_port = int(os.getenv("API_PORT", 8000))
    forwarded_allow_ips = str(os.getenv("FORWARDED_ALLOW_IPS", "172.17.0.1"))

    _app_log_format = "%(levelname)s - %(name)s - %(message)s"
    if not api_debug:
        _app_log_format = "%(asctime)s - " + _app_log_format
    
    logging.basicConfig(level=logging.INFO, format=_app_log_format, force=True)

    uvicorn_log_config = LOGGING_CONFIG.copy()
    if not api_debug:
        uvicorn_log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelprefix)s %(message)s"
        uvicorn_log_config["formatters"]["access"]["fmt"] = '%(asctime)s - %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=api_port,
        forwarded_allow_ips=(None if api_debug else forwarded_allow_ips),
        log_config=uvicorn_log_config,
    )
