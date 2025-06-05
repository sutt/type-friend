from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Determine the absolute path to the directory containing main.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup templates
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

class KeyPressEvent(BaseModel):
    key: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main HTML page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/keypress")
async def log_keypress(event: KeyPressEvent):
    """
    Receives keypress events from the client.
    """
    # For now, we'll just log the key press.
    # In the future, rate limiting can be added here.
    logger.info(f"Key pressed: {event.key}")
    return {"message": f"Key '{event.key}' received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
